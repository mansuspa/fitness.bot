import os
import logging

logger = logging.getLogger(__name__)

OPENAI_KEY     = os.getenv("OPENAI_API_KEY", "")
GEMINI_KEY     = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

FITNESS_SYSTEM_PROMPT = """Ты профессиональный фитнес-тренер и нутрициолог. Отвечай только на русском языке.
Правила ответа:
- Давай конкретные, практичные советы
- Упоминай конкретные упражнения, цифры, подходы если уместно
- Используй эмодзи для структуры
- Предупреждай о типичных ошибках
- Ответ 150-300 слов максимум
- Завершай мотивирующей фразой"""

# Кэш невалидных провайдеров в рамках одного запуска
_failed_providers: set = set()


def _build_user_prompt(goal: str, text: str, user_profile: dict = None) -> str:
    goal_names = {"gain": "набор мышечной массы", "loss": "похудение", "maintain": "поддержание формы"}
    goal_ru = goal_names.get(goal, "поддержание формы")
    profile_info = ""
    if user_profile:
        parts = []
        if user_profile.get('weight'): parts.append(f"вес {user_profile['weight']} кг")
        if user_profile.get('height'): parts.append(f"рост {user_profile['height']} см")
        if user_profile.get('age'):    parts.append(f"возраст {user_profile['age']} лет")
        if user_profile.get('gender'):
            parts.append("мужской" if user_profile['gender'] == "male" else "женский")
        if parts:
            profile_info = f"\nДанные: {', '.join(parts)}."
    return f"Цель: {goal_ru}.{profile_info}\n\nВопрос: {text}"


def _validate_openai_key() -> bool:
    """Проверяет что ключ похож на настоящий (начинается с sk-)."""
    return bool(OPENAI_KEY and OPENAI_KEY.startswith("sk-"))


def _ask_openai(prompt: str, system: str, max_tokens: int = 600) -> str:
    from openai import OpenAI, AuthenticationError
    if not _validate_openai_key():
        _failed_providers.add("openai")
        raise ValueError("OpenAI key is not valid (must start with sk-)")
    client = OpenAI(api_key=OPENAI_KEY)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except AuthenticationError as e:
        _failed_providers.add("openai")
        logger.warning("OpenAI key invalid (AuthenticationError), disabling for this session")
        raise


GEMINI_MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]


def _ask_gemini(prompt: str, system: str, max_tokens: int = 600) -> str:
    last_exc = None

    # Пробуем новый SDK (google-genai)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_KEY)
        for model_name in GEMINI_MODELS:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                )
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                logger.info(f"Gemini answered via [{model_name}]")
                return resp.text
            except Exception as e:
                logger.warning(f"Gemini [{model_name}] failed: {e}")
                last_exc = e
    except ImportError:
        pass

    # Fallback на старый SDK
    import google.generativeai as genai_old
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        genai_old.configure(api_key=GEMINI_KEY)
        for model_name in GEMINI_MODELS:
            try:
                model = genai_old.GenerativeModel(model_name, system_instruction=system)
                resp = model.generate_content(prompt)
                logger.info(f"Gemini (old SDK) answered via [{model_name}]")
                return resp.text
            except Exception as e:
                logger.warning(f"Gemini old SDK [{model_name}] failed: {e}")
                last_exc = e

    raise last_exc or RuntimeError("Gemini: all models failed")


OPENROUTER_FREE_MODELS = [
    "deepseek/deepseek-r1-0528:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "meta-llama/llama-3.1-8b-instruct",
]


def _ask_openrouter(prompt: str, system: str, max_tokens: int = 600) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=OPENROUTER_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    last_exc = None
    for model in OPENROUTER_FREE_MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            text = resp.choices[0].message.content
            if text:
                logger.info(f"OpenRouter answered via [{model}]")
                return text
        except Exception as e:
            logger.warning(f"OpenRouter [{model}] failed: {e}")
            last_exc = e
    raise last_exc or RuntimeError("OpenRouter: all models failed")


def _no_ai_response(question: str = "", goal: str = "maintain") -> str:
    """Использует встроенную базу знаний если все AI провайдеры недоступны."""
    try:
        from fitness_kb import get_ai_response, get_contextual_fallback
        kb_answer = get_ai_response(question, goal)
        if kb_answer:
            return "🤖 FITNESS AI (встроенная база знаний)\n━━━━━━━━━━━━━━━━━━━━\n\n" + kb_answer
        return get_contextual_fallback(question, goal)
    except Exception:
        pass
    return (
        "⚠️ AI провайдеры временно недоступны.\n\n"
        "💡 Проверь API ключи в настройках.\n"
        "Попробуй задать вопрос позже! 💪"
    )


def _resolve_order(provider: str) -> list:
    """Возвращает порядок провайдеров с учётом выбора и доступности ключей."""
    if provider == "openai":
        order = ["openai", "gemini", "openrouter"]
    elif provider == "gemini":
        order = ["gemini", "openai", "openrouter"]
    elif provider == "openrouter":
        order = ["openrouter", "gemini", "openai"]
    else:
        # auto: сначала Gemini (бесплатный), потом OpenRouter, потом OpenAI
        order = []
        if GEMINI_KEY:      order.append("gemini")
        if OPENROUTER_KEY:  order.append("openrouter")
        if OPENAI_KEY:      order.append("openai")

    # Убираем тех у кого нет ключа или кто уже сломан
    filtered = []
    for p in order:
        if p in _failed_providers:
            continue
        if p == "openai"     and not OPENAI_KEY:     continue
        if p == "gemini"     and not GEMINI_KEY:      continue
        if p == "openrouter" and not OPENROUTER_KEY:  continue
        filtered.append(p)
    return filtered or order  # если всё отфильтровалось — возвращаем исходный


def _call_provider(prov: str, prompt: str, system: str, max_tokens: int = 600) -> str:
    if prov == "openai":
        return _ask_openai(prompt, system, max_tokens)
    elif prov == "gemini":
        return _ask_gemini(prompt, system, max_tokens)
    elif prov == "openrouter":
        return _ask_openrouter(prompt, system, max_tokens)
    raise ValueError(f"Unknown provider: {prov}")


def fitness_ai(goal: str, text: str, user_profile: dict = None, provider: str = "auto") -> str:
    prompt = _build_user_prompt(goal, text, user_profile)
    system = FITNESS_SYSTEM_PROMPT
    for prov in _resolve_order(provider):
        try:
            result = _call_provider(prov, prompt, system, max_tokens=600)
            logger.info(f"AI answered via [{prov}]")
            return result
        except Exception as e:
            logger.error(f"[{prov}] error: {e}")
            continue
    return _no_ai_response(text, goal)


def generate_workout_plan(goal: str, profile: dict, provider: str = "auto") -> str:
    goal_names = {"gain": "набор мышечной массы", "loss": "похудение", "maintain": "поддержание формы"}
    prompt = (
        f"Составь персональный план тренировок на неделю.\n"
        f"Цель: {goal_names.get(goal, 'поддержание')}.\n"
        f"Вес: {profile.get('weight', '?')} кг, рост: {profile.get('height', '?')} см, "
        f"возраст: {profile.get('age', '?')}.\n"
        f"Формат: каждый день недели с конкретными упражнениями, подходами и повторениями.\n"
        f"Используй эмодзи. Ответ на русском. Максимум 400 слов."
    )
    system = "Ты профессиональный фитнес-тренер. Отвечай только на русском языке."
    for prov in _resolve_order(provider):
        try:
            return _call_provider(prov, prompt, system, max_tokens=800)
        except Exception as e:
            logger.error(f"[{prov}] workout plan error: {e}")
    return None


def generate_meal_plan(goal: str, profile: dict, calories: int, provider: str = "auto") -> str:
    goal_names = {"gain": "набор мышечной массы", "loss": "похудение", "maintain": "поддержание формы"}
    prompt = (
        f"Составь план питания на день.\n"
        f"Цель: {goal_names.get(goal, 'поддержание')}.\n"
        f"Целевые калории: {calories} ккал.\n"
        f"Вес: {profile.get('weight', '?')} кг.\n"
        f"Включи завтрак, обед, ужин, перекусы с калориями каждого приёма.\n"
        f"Используй эмодзи. Ответ на русском. Максимум 350 слов."
    )
    system = "Ты профессиональный нутрициолог. Отвечай только на русском языке."
    for prov in _resolve_order(provider):
        try:
            return _call_provider(prov, prompt, system, max_tokens=700)
        except Exception as e:
            logger.error(f"[{prov}] meal plan error: {e}")
    return None


def get_available_providers() -> list:
    result = []
    if GEMINI_KEY:      result.append("gemini")
    if OPENROUTER_KEY:  result.append("openrouter")
    if OPENAI_KEY and "openai" not in _failed_providers:
        result.append("openai")
    return result
