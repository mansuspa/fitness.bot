from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery,
)

from database import Database
from ai import fitness_ai, generate_workout_plan, generate_meal_plan, get_available_providers
from exercises_data import EXERCISES, MUSCLE_GROUPS
from nutrition_data import FOODS, MEAL_PLANS, NUTRITION_RULES
from programs_data import PROGRAMS
from config import ADMIN_IDS

router = Router()
db = Database()

# ╔══════════════════════════════════════╗
#           ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ╚══════════════════════════════════════╝

def get_plans():
    return {
        "month":  {"label": "1 месяц",  "days": 30,  "stars": int(db.get_setting("price_month_stars", "75"))},
        "3month": {"label": "3 месяца", "days": 90,  "stars": int(db.get_setting("price_3month_stars", "175"))},
        "year":   {"label": "1 год",    "days": 365, "stars": int(db.get_setting("price_year_stars", "499"))},
    }

def paywall_check(uid: int) -> bool:
    """True = доступ разрешён"""
    if uid in ADMIN_IDS:
        return True
    if db.is_banned(uid):
        return False
    return db.is_active(uid)

def subscription_plans_kb():
    plans = get_plans()
    saving_3m = round((1 - plans['3month']['stars'] / (plans['month']['stars'] * 3)) * 100)
    saving_yr  = round((1 - plans['year']['stars']  / (plans['month']['stars'] * 12)) * 100)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"⭐ {plans['month']['stars']} Stars — 1 месяц",
            callback_data="buy_month")],
        [InlineKeyboardButton(
            text=f"⭐ {plans['3month']['stars']} Stars — 3 месяца  (-{saving_3m}%)",
            callback_data="buy_3month")],
        [InlineKeyboardButton(
            text=f"⭐ {plans['year']['stars']} Stars — 1 год  (-{saving_yr}%)",
            callback_data="buy_year")],
    ])

def back_kb(cb, label="◀️ Назад"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=cb)]])

def back_row(cb, label="◀️ Назад"):
    return [InlineKeyboardButton(text=label, callback_data=cb)]

def premium_lock_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Оформить подписку", callback_data="sub_plans")]
    ])

# ╔══════════════════════════════════════╗
#                  FSM
# ╚══════════════════════════════════════╝
class ProfileFSM(StatesGroup):
    gender = State()
    age    = State()
    height = State()
    weight = State()

class AdminFSM(StatesGroup):
    broadcast    = State()
    grant_uid    = State()
    grant_days   = State()
    revoke_uid   = State()
    ban_uid      = State()
    unban_uid    = State()
    msg_uid      = State()
    msg_text     = State()
    set_key      = State()
    set_value    = State()

class FoodDiaryFSM(StatesGroup):
    meal_type = State()
    food_name = State()
    calories  = State()

class MeasureFSM(StatesGroup):
    chest = State()
    waist = State()
    hips  = State()
    bicep = State()

# ╔══════════════════════════════════════╗
#              ГЛАВНОЕ МЕНЮ
# ╚══════════════════════════════════════╝
def main_menu(is_admin=False):
    kb = [
        [KeyboardButton(text="💪 Набор массы"),   KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Поддержание")],
        [KeyboardButton(text="🏋️ Упражнения"),   KeyboardButton(text="🍽 Питание")],
        [KeyboardButton(text="📅 Программа"),     KeyboardButton(text="🤖 AI тренер")],
        [KeyboardButton(text="🔥 Калории"),       KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="👤 Профиль"),       KeyboardButton(text="⭐ Подписка")],
        [KeyboardButton(text="📋 Статистика"),    KeyboardButton(text="📓 Дневник")],
        [KeyboardButton(text="💧 Вода"),          KeyboardButton(text="📐 Замеры")],
        [KeyboardButton(text="⚖️ BMI"),           KeyboardButton(text="🔗 Реферал")],
        [KeyboardButton(text="🔔 Напоминания")],
    ]
    if is_admin:
        kb.append([KeyboardButton(text="🔑 Админ")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def no_sub_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⭐ Купить подписку")]],
        resize_keyboard=True
    )

# ╔══════════════════════════════════════╗
#                  /start
# ╚══════════════════════════════════════╝
@router.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.from_user.id
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1][3:])
            if referrer_id == uid:
                referrer_id = None
        except ValueError:
            referrer_id = None

    is_new = not db.get_user(uid)
    db.add_user(uid, message.from_user.username, message.from_user.first_name, referrer_id)
    is_admin = uid in ADMIN_IDS
    name = message.from_user.first_name or "друг"
    trial_days = int(db.get_setting("trial_days", "3"))
    welcome = db.get_setting("welcome_text", "👋 Добро пожаловать!")

    if db.is_banned(uid):
        return await message.answer("🚫 Ваш аккаунт заблокирован.")

    if is_new:
        await message.answer(
            f"{welcome}\n\n"
            f"👋 Привет, {name}!\n\n"
            f"🎁 Тебе активирован БЕСПЛАТНЫЙ пробный период на {trial_days} дней!\n\n"
            f"🏋️ FITNESS AI PRO — твой личный тренер:\n"
            f"• 💪 Планы тренировок и питания\n"
            f"• 🤖 AI тренер (OpenAI / Gemini / OpenRouter)\n"
            f"• 📊 Трекинг прогресса, калорий, воды\n"
            f"• 📐 Замеры тела и BMI\n"
            f"• 🔗 Реферальная программа\n\n"
            f"{'🔑 Ты администратор бота.\n\n' if is_admin else ''}"
            f"Начни с заполнения профиля → «👤 Профиль» 👇",
            reply_markup=main_menu(is_admin)
        )
    else:
        sub = db.get_subscription(uid)
        if not db.is_active(uid):
            await message.answer(
                f"👋 С возвращением, {name}!\n\n"
                f"⏰ Твой пробный период закончился.\n"
                f"Оформи подписку для продолжения:",
                reply_markup=subscription_plans_kb()
            )
        else:
            days = db.days_left(uid)
            await message.answer(
                f"👋 С возвращением, {name}! 💪\n"
                f"{'⭐ Статус: Premium' if db.is_premium(uid) else f'🎁 Пробный период: {days} дн.'}\n",
                reply_markup=main_menu(is_admin)
            )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    if db.is_banned(message.from_user.id):
        return
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer("📱 Главное меню:", reply_markup=main_menu(is_admin))

# ╔══════════════════════════════════════╗
#         ПРОВЕРКА ПОДПИСКИ (мидлвар)
# ╚══════════════════════════════════════╝
async def check_access(message: Message) -> bool:
    uid = message.from_user.id
    if db.is_banned(uid):
        await message.answer("🚫 Ваш аккаунт заблокирован.")
        return False
    if not paywall_check(uid):
        days_sub = db.get_subscription(uid)
        text = (
            "⏰ ПРОБНЫЙ ПЕРИОД ЗАКОНЧИЛСЯ\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Оформи подписку чтобы продолжить пользоваться ботом.\n\n"
            "Что включено:\n"
            "💪 Планы тренировок и питания\n"
            "🤖 AI тренер (3 провайдера)\n"
            "📊 Трекинг прогресса\n"
            "📐 Замеры тела и BMI\n"
            "🔗 Реферальные бонусы\n\n"
            "Выбери план:"
        ) if days_sub else (
            "🔒 Нет активной подписки.\n\nОформи:"
        )
        await message.answer(text, reply_markup=subscription_plans_kb())
        return False
    return True

# ╔══════════════════════════════════════╗
#                   ЦЕЛИ
# ╚══════════════════════════════════════╝
@router.message(F.text.in_(["💪 Набор массы", "🔥 Похудение", "⚖️ Поддержание"]))
async def set_goal(message: Message):
    if not await check_access(message):
        return
    uid = message.from_user.id
    goal_map = {"💪 Набор массы": "gain", "🔥 Похудение": "loss", "⚖️ Поддержание": "maintain"}
    goal = goal_map[message.text]
    db.update_user(uid, goal=goal)
    info = {
        "gain":     ("💪 НАБОР МАССЫ",    "Профицит +300–500 ккал. Белок 2.0–2.2 г/кг. Силовые 4–5 раз/нед."),
        "loss":     ("🔥 ПОХУДЕНИЕ",       "Дефицит –300–500 ккал. Белок 2.2–2.4 г/кг. Кардио 4–5 раз/нед."),
        "maintain": ("⚖️ ПОДДЕРЖАНИЕ",    "Баланс калорий. Белок 1.6–2.0 г/кг. 3 тренировки/нед."),
    }
    title, desc = info[goal]
    await message.answer(f"{title}\n━━━━━━━━━━━━━━━━━━━━\n✅ Цель установлена!\n\n📌 {desc}")

# ╔══════════════════════════════════════╗
#                 ПРОФИЛЬ
# ╚══════════════════════════════════════╝
@router.message(F.text == "👤 Профиль")
async def profile_menu(message: Message):
    if not await check_access(message):
        return
    uid = message.from_user.id
    user = db.get_user(uid)
    sub = db.get_subscription(uid)
    goal_names = {"gain": "💪 Набор массы", "loss": "🔥 Похудение", "maintain": "⚖️ Поддержание"}
    gender_names = {"male": "👨 Мужчина", "female": "👩 Женщина"}
    is_prem = db.is_premium(uid)
    is_trial_active = db.is_trial(uid)
    days = db.days_left(uid)

    lines = ["👤 МОЙ ПРОФИЛЬ", "━━━━━━━━━━━━━━━━━━━━",
             f"🎯 Цель: {goal_names.get(user.get('goal','maintain'), '—')}"]
    if is_prem:
        lines.append(f"⭐ Статус: Premium  ({days} дн.)")
    elif is_trial_active:
        lines.append(f"🎁 Пробный период: {days} дн.")
    if sub and sub.get('expires_at'):
        from datetime import datetime
        exp = datetime.fromisoformat(sub['expires_at'])
        lines.append(f"📅 До: {exp.strftime('%d.%m.%Y')}")
    for field, emoji, name in [('gender','👤','Пол'), ('age','🎂','Возраст'), ('height','📏','Рост'), ('weight','⚖️','Вес')]:
        if user.get(field):
            val = gender_names.get(user[field], user[field]) if field == 'gender' else (f"{user[field]} лет" if field == 'age' else (f"{user[field]} см" if field == 'height' else f"{user[field]} кг"))
            lines.append(f"{emoji} {name}: {val}")
    if user.get('weight') and user.get('height'):
        bmi = user['weight'] / (user['height'] / 100) ** 2
        label = "Недовес" if bmi < 18.5 else "Норма ✅" if bmi < 25 else "Избыток ⚠️" if bmi < 30 else "Ожирение 🔴"
        lines.append(f"📊 BMI: {bmi:.1f} ({label})")
    ref_count = db.get_referral_count(uid)
    if ref_count:
        lines.append(f"🔗 Рефералов: {ref_count}")
    lines += ["", "━━━━━━━━━━━━━━━━━━━━", "✏️ Изменить: /setprofile"]
    await message.answer("\n".join(lines))

@router.message(Command("setprofile"))
async def start_profile(message: Message, state: FSMContext):
    if not await check_access(message):
        return
    await state.set_state(ProfileFSM.gender)
    await message.answer("Шаг 1/4 — Выбери пол:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужчина", callback_data="gender_male"),
         InlineKeyboardButton(text="👩 Женщина", callback_data="gender_female")]
    ]))

@router.callback_query(F.data.in_(["gender_male", "gender_female"]), ProfileFSM.gender)
async def profile_gender(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data.replace("gender_", ""))
    await state.set_state(ProfileFSM.age)
    await callback.message.edit_text("Шаг 2/4 — Введи возраст (лет):")
    await callback.answer()

@router.message(ProfileFSM.age)
async def profile_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        assert 10 <= age <= 100
    except:
        return await message.answer("❌ Введи возраст числом (10–100):")
    await state.update_data(age=age)
    await state.set_state(ProfileFSM.height)
    await message.answer("Шаг 3/4 — Введи рост (см):")

@router.message(ProfileFSM.height)
async def profile_height(message: Message, state: FSMContext):
    try:
        h = float(message.text.replace(',', '.'))
        assert 100 <= h <= 250
    except:
        return await message.answer("❌ Введи рост в см (100–250):")
    await state.update_data(height=h)
    await state.set_state(ProfileFSM.weight)
    await message.answer("Шаг 4/4 — Введи вес (кг):")

@router.message(ProfileFSM.weight)
async def profile_weight(message: Message, state: FSMContext):
    try:
        w = float(message.text.replace(',', '.'))
        assert 30 <= w <= 300
    except:
        return await message.answer("❌ Введи вес в кг (30–300):")
    data = await state.get_data()
    data['weight'] = w
    uid = message.from_user.id
    db.update_user(uid, **data)
    db.add_weight(uid, w)
    await state.clear()
    h, a, g = data['height'], data['age'], data['gender']
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if g == 'male' else -161)
    norm = int(bmr * 1.5)
    user = db.get_user(uid)
    mult = {"gain": 1.15, "loss": 0.85, "maintain": 1.0}.get(user.get('goal','maintain'), 1.0)
    bmi = w / (h / 100) ** 2
    await message.answer(
        f"✅ ПРОФИЛЬ СОХРАНЁН!\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{'👨' if g=='male' else '👩'} {'Мужчина' if g=='male' else 'Женщина'} | {a} лет | {h} см | {w} кг\n"
        f"📊 BMI: {bmi:.1f}\n\n"
        f"🔥 Калории по целям:\n"
        f"💪 Набор: {norm + 400} | 🔥 Похудение: {norm - 400} | ⚖️ Поддержание: {norm}\n"
        f"🎯 Твоя цель: {int(norm * mult)} ккал/день"
    )

# ╔══════════════════════════════════════╗
#               УПРАЖНЕНИЯ
# ╚══════════════════════════════════════╝
def exercises_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Грудь",   callback_data="ex_chest"),
         InlineKeyboardButton(text="🏋️ Спина",   callback_data="ex_back")],
        [InlineKeyboardButton(text="🦵 Ноги",    callback_data="ex_legs"),
         InlineKeyboardButton(text="💪 Плечи",   callback_data="ex_shoulders")],
        [InlineKeyboardButton(text="💪 Бицепс",  callback_data="ex_biceps"),
         InlineKeyboardButton(text="💪 Трицепс", callback_data="ex_triceps")],
        [InlineKeyboardButton(text="🔥 Пресс",   callback_data="ex_press"),
         InlineKeyboardButton(text="🏃 Кардио",  callback_data="ex_cardio")],
    ])

def exercise_list_kb(gk):
    rows = [[InlineKeyboardButton(text=f"• {ex['name']}", callback_data=f"exdetail_{gk}_{i}")]
            for i, ex in enumerate(EXERCISES[gk]["exercises"])]
    rows.append(back_row("back_exercises", "◀️ К группам"))
    return InlineKeyboardMarkup(inline_keyboard=rows)

def exercise_detail_kb(gk):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К списку", callback_data=f"ex_{gk}")],
        [InlineKeyboardButton(text="🏠 К группам", callback_data="back_exercises")],
    ])

@router.message(F.text == "🏋️ Упражнения")
async def exercises_main(message: Message):
    if not await check_access(message): return
    await message.answer("🏋️ УПРАЖНЕНИЯ\n━━━━━━━━━━━━━━━━━━━━\nВыбери группу мышц:", reply_markup=exercises_menu_kb())

@router.callback_query(F.data == "back_exercises")
async def back_to_exercises(callback: CallbackQuery):
    await callback.message.edit_text("🏋️ УПРАЖНЕНИЯ\n━━━━━━━━━━━━━━━━━━━━\nВыбери группу мышц:", reply_markup=exercises_menu_kb())

@router.callback_query(F.data.in_(list(MUSCLE_GROUPS.keys())))
async def show_exercise_list(callback: CallbackQuery):
    gk = MUSCLE_GROUPS[callback.data]
    g = EXERCISES[gk]
    await callback.message.edit_text(
        f"{g['name']}\n━━━━━━━━━━━━━━━━━━━━\n🎯 {g['muscles']}\n\nВыбери упражнение:",
        reply_markup=exercise_list_kb(gk)
    )

@router.callback_query(F.data.startswith("exdetail_"))
async def show_exercise_detail(callback: CallbackQuery):
    _, gk, idx = callback.data.split("_", 2)
    ex = EXERCISES[gk]["exercises"][int(idx)]
    await callback.message.edit_text(
        f"🏋️ {ex['name']}\n━━━━━━━━━━━━━━━━━━━━\n🎯 {ex['target']}\n📊 {ex['sets']}\n\n📝 КАК ДЕЛАТЬ:\n{ex['how']}",
        reply_markup=exercise_detail_kb(gk)
    )

# ╔══════════════════════════════════════╗
#                 ПИТАНИЕ
# ╚══════════════════════════════════════╝
def nutrition_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Рацион по цели", callback_data="nut_plan")],
        [InlineKeyboardButton(text="🥩 Белки",    callback_data="nut_proteins"),
         InlineKeyboardButton(text="🌾 Углеводы", callback_data="nut_carbs")],
        [InlineKeyboardButton(text="🥑 Жиры",     callback_data="nut_fats"),
         InlineKeyboardButton(text="🥦 Овощи",    callback_data="nut_vegetables")],
        [InlineKeyboardButton(text="🏆 Правила питания", callback_data="nut_rules")],
        [InlineKeyboardButton(text="🤖 AI план питания", callback_data="nut_ai_plan")],
    ])

def back_to_nutrition_kb():
    return back_kb("back_nutrition", "◀️ К питанию")

@router.message(F.text == "🍽 Питание")
async def nutrition_main(message: Message):
    if not await check_access(message): return
    await message.answer("🍽 ПИТАНИЕ\n━━━━━━━━━━━━━━━━━━━━\nВсё о правильном питании:", reply_markup=nutrition_menu_kb())

@router.callback_query(F.data == "back_nutrition")
async def back_to_nutrition(callback: CallbackQuery):
    await callback.message.edit_text("🍽 ПИТАНИЕ\n━━━━━━━━━━━━━━━━━━━━", reply_markup=nutrition_menu_kb())

@router.callback_query(F.data == "nut_plan")
async def nutrition_plan(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    plan = MEAL_PLANS[user.get("goal", "maintain")]
    lines = [plan['title'], "━━━━━━━━━━━━━━━━━━━━", f"📌 {plan['rule']}\n"]
    for name, content in plan["meals"]:
        lines.append(f"{name}\n{content}\n")
    lines += [plan["total"] + "\n", "💡 СОВЕТЫ:"] + plan["tips"]
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_nutrition_kb())

@router.callback_query(F.data.in_(["nut_proteins", "nut_carbs", "nut_fats", "nut_vegetables"]))
async def nutrition_food_list(callback: CallbackQuery):
    km = {"nut_proteins": "proteins", "nut_carbs": "carbs", "nut_fats": "fats", "nut_vegetables": "vegetables"}
    food = FOODS[km[callback.data]]
    lines = [food["name"], "━━━━━━━━━━━━━━━━━━━━", f"ℹ️ {food['desc']}\n"]
    for n, i in food["list"]:
        lines.append(f"• {n}\n  {i}")
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_nutrition_kb())

@router.callback_query(F.data == "nut_rules")
async def nutrition_rules(callback: CallbackQuery):
    await callback.message.edit_text(NUTRITION_RULES, reply_markup=back_to_nutrition_kb())

@router.callback_query(F.data == "nut_ai_plan")
async def nutrition_ai_plan(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.edit_text("⏳ AI составляет план питания...")
    user = db.get_user(uid)
    provider = user.get("ai_provider", "auto")
    if db.profile_complete(uid):
        w, h, a, g = user['weight'], user['height'], user['age'], user.get('gender','male')
        bmr = 10*w + 6.25*h - 5*a + (5 if g == 'male' else -161)
        mult = {"gain": 1.15, "loss": 0.85, "maintain": 1.0}.get(user.get('goal','maintain'), 1.0)
        plan = generate_meal_plan(user.get('goal','maintain'), user, int(bmr * 1.5 * mult), provider)
    else:
        plan = generate_meal_plan(user.get('goal','maintain'), {}, 2000, provider)
    text = f"🤖 AI ПЛАН ПИТАНИЯ\n━━━━━━━━━━━━━━━━━━━━\n{plan}" if plan else "❌ Ошибка AI. Попробуй позже."
    await callback.message.edit_text(text, reply_markup=back_to_nutrition_kb())
    await callback.answer()

# ╔══════════════════════════════════════╗
#          ПРОГРАММЫ ТРЕНИРОВОК
# ╚══════════════════════════════════════╝
def programs_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Набор массы",  callback_data="prog_gain")],
        [InlineKeyboardButton(text="🔥 Похудение",    callback_data="prog_loss")],
        [InlineKeyboardButton(text="⚖️ Поддержание",  callback_data="prog_maintain")],
        [InlineKeyboardButton(text="🤖 AI программа", callback_data="prog_ai")],
    ])

def program_days_kb(goal, program):
    rows = [[InlineKeyboardButton(text=f"{day}  {title}", callback_data=f"progday_{goal}_{day}")]
            for day, (title, _) in program["schedule"].items()]
    rows.append(back_row("back_programs", "◀️ К программам"))
    return InlineKeyboardMarkup(inline_keyboard=rows)

def back_to_program_kb(goal):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К расписанию", callback_data=f"prog_{goal}")],
        [InlineKeyboardButton(text="📅 Все программы", callback_data="back_programs")],
    ])

@router.message(F.text == "📅 Программа")
async def programs_main(message: Message):
    if not await check_access(message): return
    await message.answer("📅 ПРОГРАММЫ\n━━━━━━━━━━━━━━━━━━━━\nГотовые программы на 7 дней:", reply_markup=programs_menu_kb())

@router.callback_query(F.data == "back_programs")
async def back_to_programs(callback: CallbackQuery):
    await callback.message.edit_text("📅 ПРОГРАММЫ\n━━━━━━━━━━━━━━━━━━━━", reply_markup=programs_menu_kb())

@router.callback_query(F.data.in_(["prog_gain", "prog_loss", "prog_maintain"]))
async def show_program(callback: CallbackQuery):
    goal = callback.data.replace("prog_", "")
    prog = PROGRAMS[goal]
    lines = [prog["title"], "━━━━━━━━━━━━━━━━━━━━", f"📌 {prog['subtitle']}", f"🎯 {prog['goal']}\n", "📋 ПРАВИЛА:"]
    lines += prog["rules"] + ["\n👇 Выбери день:"]
    await callback.message.edit_text("\n".join(lines), reply_markup=program_days_kb(goal, prog))

@router.callback_query(F.data.startswith("progday_"))
async def show_program_day(callback: CallbackQuery):
    _, goal, day = callback.data.split("_", 2)
    prog = PROGRAMS[goal]
    title, exercises = prog["schedule"][day]
    lines = [f"📅 {day}  {title}", "━━━━━━━━━━━━━━━━━━━━"]
    for name, sets in exercises:
        lines.append(f"▸ {name}  {'— ' + sets if sets else ''}")
    lines.append(f"\n💪 {prog['title']}")
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_program_kb(goal))

@router.callback_query(F.data == "prog_ai")
async def program_ai(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.edit_text("⏳ AI составляет программу тренировок...")
    user = db.get_user(uid)
    plan = generate_workout_plan(user.get('goal','maintain'), user, user.get("ai_provider","auto"))
    text = f"🤖 AI ПРОГРАММА\n━━━━━━━━━━━━━━━━━━━━\n{plan}" if plan else "❌ Ошибка AI. Попробуй позже."
    await callback.message.edit_text(text, reply_markup=back_to_program_kb('gain'))
    await callback.answer()

# ╔══════════════════════════════════════╗
#              AI ТРЕНЕР
# ╚══════════════════════════════════════╝
def ai_provider_kb(current: str = "auto"):
    available = get_available_providers()
    labels = {"auto": "🔄 Авто", "openai": "🟢 OpenAI (GPT-4o)", "gemini": "🔵 Gemini 2.5", "openrouter": "🟠 OpenRouter"}
    rows = []
    for prov in (["auto"] + available):
        lbl = ("✅ " if prov == current else "") + labels.get(prov, prov)
        rows.append([InlineKeyboardButton(text=lbl, callback_data=f"ai_prov_{prov}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(F.text == "🤖 AI тренер")
async def ai_prompt(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    user = db.get_user(uid)
    current = user.get("ai_provider", "auto")
    prov_name = {"auto": "Авто", "openai": "OpenAI", "gemini": "Gemini", "openrouter": "OpenRouter"}.get(current, current)
    await message.answer(
        "🤖 AI ТРЕНЕР\n━━━━━━━━━━━━━━━━━━━━\n"
        "Задай любой вопрос о фитнесе.\nНапиши 🤖 и вопрос:\n\n"
        "• 🤖 как накачать плечи?\n• 🤖 что есть до тренировки?\n"
        "• 🤖 составь план на неделю\n\n"
        f"🧠 Провайдер: {prov_name}\nПереключить:",
        reply_markup=ai_provider_kb(current)
    )

@router.callback_query(F.data.startswith("ai_prov_"))
async def set_ai_provider(callback: CallbackQuery):
    uid = callback.from_user.id
    prov = callback.data.replace("ai_prov_", "")
    db.update_user(uid, ai_provider=prov)
    await callback.message.edit_reply_markup(reply_markup=ai_provider_kb(prov))
    names = {"auto": "Авто", "openai": "OpenAI", "gemini": "Gemini", "openrouter": "OpenRouter"}
    await callback.answer(f"✅ Провайдер: {names.get(prov, prov)}")

@router.message(F.text.startswith("🤖"))
async def ai_answer(message: Message):
    if not await check_access(message): return
    text = message.text.replace("🤖", "").strip()
    if not text:
        return await message.answer("Напиши вопрос после 🤖\nПример: 🤖 как накачать плечи?")
    uid = message.from_user.id
    user = db.get_user(uid)
    provider = user.get("ai_provider", "auto")
    emoji = {"auto": "🔄", "openai": "🟢", "gemini": "🔵", "openrouter": "🟠"}.get(provider, "🤖")
    await message.answer(f"⏳ {emoji} AI думает...")
    answer = fitness_ai(user.get("goal","maintain"), text, user, provider)
    await message.answer(f"🤖 AI ТРЕНЕР\n━━━━━━━━━━━━━━━━━━━━\n{answer}")

# ╔══════════════════════════════════════╗
#              КАЛОРИИ & BMI
# ╚══════════════════════════════════════╝
@router.message(F.text == "🔥 Калории")
async def calories_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    user = db.get_user(uid)
    today_cal = db.get_today_calories(uid)
    if db.profile_complete(uid):
        w,h,a,g = user['weight'],user['height'],user['age'],user.get('gender','male')
        bmr = 10*w + 6.25*h - 5*a + (5 if g=='male' else -161)
        norm = int(bmr * 1.5)
        mult = {"gain":1.15,"loss":0.85,"maintain":1.0}.get(user.get('goal','maintain'),1.0)
        target = int(norm * mult)
        remaining = target - today_cal
        bar_filled = min(20, int(today_cal / target * 20)) if target else 0
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        await message.answer(
            f"🔥 МОИ КАЛОРИИ\n━━━━━━━━━━━━━━━━━━━━\n"
            f"[{bar}]\n"
            f"📊 Сегодня: {today_cal} / {target} ккал\n"
            f"{'✅ В норме' if remaining >= 0 else '⚠️ Превышено'}: {abs(remaining)} ккал\n\n"
            f"💪 Набор: {norm+400} | 🔥 Похудение: {norm-400}\n\n"
            f"💾 /cal 2200 — записать\n📈 /calhistory — история"
        )
    else:
        await message.answer(
            "🔥 КАЛОРИИ\n━━━━━━━━━━━━━━━━━━━━\n"
            "Заполни профиль → «👤 Профиль»\n\n"
            "Или введи вручную: вес рост возраст\n"
            "Пример: 75 180 25\n\n"
            "💾 /cal 2200 | 📈 /calhistory"
        )

@router.message(F.text.regexp(r"^\d+\s\d+\s\d+$"))
async def calc_calories(message: Message):
    if not await check_access(message): return
    w,h,a = map(int, message.text.split())
    user = db.get_user(message.from_user.id)
    g = user.get('gender','male')
    bmr = 10*w + 6.25*h - 5*a + (5 if g=='male' else -161)
    norm = int(bmr * 1.5)
    bmi = w / (h/100)**2
    label = "Недовес" if bmi<18.5 else "Норма" if bmi<25 else "Избыток" if bmi<30 else "Ожирение"
    await message.answer(
        f"📊 РАСЧЁТ\n━━━━━━━━━━━━━━━━━━━━\n"
        f"⚖️ {w} кг | 📏 {h} см | 🎂 {a} лет\n"
        f"📊 BMI: {bmi:.1f} ({label})\n\n"
        f"💪 Набор: {norm+400} | 🔥 Похудение: {norm-400} | ⚖️ Норма: {norm} ккал\n\n"
        f"💾 /cal {norm}"
    )

@router.message(F.text == "⚖️ BMI")
async def bmi_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    user = db.get_user(uid)
    if user.get('weight') and user.get('height'):
        w,h = user['weight'], user['height']
        bmi = w / (h/100)**2
        if bmi < 18.5:    status,advice = "📉 Недостаточный вес", "Увеличь калорийность рациона на 300–500 ккал. Акцент на белок и силовые."
        elif bmi < 25:    status,advice = "✅ Нормальный вес",     "Отлично! Поддерживай баланс питания и регулярные тренировки."
        elif bmi < 30:    status,advice = "⚠️ Избыточный вес",     "Дефицит 300–500 ккал/день + кардио 3–4 раза в неделю."
        else:             status,advice = "🔴 Ожирение",           "Проконсультируйся с врачом. Начни с ходьбы 30 мин/день."
        await message.answer(
            f"⚖️ BMI КАЛЬКУЛЯТОР\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Вес: {w} кг | Рост: {h} см\n\n"
            f"📊 BMI: {bmi:.1f}\n{status}\n\n"
            f"💡 {advice}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"< 18.5 — Недовес | 18.5–24.9 — Норма ✅\n25–29.9 — Избыток | ≥ 30 — Ожирение"
        )
    else:
        await message.answer(
            "⚖️ BMI\n━━━━━━━━━━━━━━━━━━━━\n"
            "Введи: вес рост\nПример: 75 180\n\n"
            "Или заполни профиль → /setprofile"
        )

@router.message(F.text.regexp(r"^\d+\s\d+$"))
async def calc_bmi_inline(message: Message):
    if not await check_access(message): return
    w,h = map(float, message.text.split())
    bmi = w / (h/100)**2
    label = "Недовес 📉" if bmi<18.5 else "Норма ✅" if bmi<25 else "Избыток ⚠️" if bmi<30 else "Ожирение 🔴"
    await message.answer(f"⚖️ BMI: {bmi:.1f} — {label}")

# ╔══════════════════════════════════════╗
#              ДНЕВНИК ПИТАНИЯ
# ╚══════════════════════════════════════╝
def diary_meal_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍳 Завтрак", callback_data="diary_breakfast"),
         InlineKeyboardButton(text="🍽 Обед",    callback_data="diary_lunch")],
        [InlineKeyboardButton(text="🍴 Ужин",    callback_data="diary_dinner"),
         InlineKeyboardButton(text="🥜 Перекус", callback_data="diary_snack")],
    ])

@router.message(F.text == "📓 Дневник")
async def diary_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    entries = db.get_today_diary(uid)
    total = sum(e['calories'] for e in entries)
    meal_names = {"breakfast":"🍳 Завтрак","lunch":"🍽 Обед","dinner":"🍴 Ужин","snack":"🥜 Перекус"}
    lines = ["📓 ДНЕВНИК ПИТАНИЯ\n━━━━━━━━━━━━━━━━━━━━\nСегодня:\n"]
    if entries:
        for e in entries:
            lines.append(f"{meal_names.get(e['meal_type'], e['meal_type'])}: {e['food_name']} — {e['calories']} ккал")
        lines.append(f"\n📊 Итого: {total} ккал")
    else:
        lines.append("Записей нет — добавь первый приём пищи!")
    lines.append("\n\n📝 Добавить:")
    await message.answer("\n".join(lines), reply_markup=diary_meal_kb())

@router.callback_query(F.data.startswith("diary_"))
async def diary_add_meal(callback: CallbackQuery, state: FSMContext):
    meal_type = callback.data.replace("diary_", "")
    await state.update_data(meal_type=meal_type)
    await state.set_state(FoodDiaryFSM.food_name)
    await callback.message.answer("📝 Напиши название блюда:")
    await callback.answer()

@router.message(FoodDiaryFSM.food_name)
async def diary_food_name(message: Message, state: FSMContext):
    await state.update_data(food_name=message.text.strip())
    await state.set_state(FoodDiaryFSM.calories)
    await message.answer("Сколько калорий? (число)")

@router.message(FoodDiaryFSM.calories)
async def diary_calories(message: Message, state: FSMContext):
    try:
        cal = int(message.text.strip())
    except:
        return await message.answer("❌ Введи число:")
    data = await state.get_data()
    uid = message.from_user.id
    db.add_food_entry(uid, data['meal_type'], data['food_name'], cal)
    db.add_calories(uid, cal, data['food_name'])
    await state.clear()
    names = {"breakfast":"🍳 Завтрак","lunch":"🍽 Обед","dinner":"🍴 Ужин","snack":"🥜 Перекус"}
    today = db.get_today_calories(uid)
    await message.answer(
        f"✅ {names.get(data['meal_type'],'')} — {data['food_name']} — {cal} ккал\n📊 Сегодня: {today} ккал",
        reply_markup=diary_meal_kb()
    )

# ╔══════════════════════════════════════╗
#              ТРЕКЕР ВОДЫ
# ╚══════════════════════════════════════╝
def water_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💧 200 мл", callback_data="water_200"),
         InlineKeyboardButton(text="💧 300 мл", callback_data="water_300"),
         InlineKeyboardButton(text="💧 500 мл", callback_data="water_500")],
        [InlineKeyboardButton(text="🥤 Стакан 250 мл", callback_data="water_250"),
         InlineKeyboardButton(text="🍶 Бутылка 1л",    callback_data="water_1000")],
    ])

@router.message(F.text == "💧 Вода")
async def water_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    today_ml = db.get_today_water(uid)
    norm = 2500
    pct = min(100, int(today_ml / norm * 100))
    bar_filled = min(20, int(pct / 5))
    bar = "💧" * bar_filled + "░" * (20 - bar_filled)
    await message.answer(
        f"💧 ТРЕКЕР ВОДЫ\n━━━━━━━━━━━━━━━━━━━━\n"
        f"[{bar}]\n"
        f"Сегодня: {today_ml} мл / {norm} мл ({pct}%)\n\n"
        f"{'✅ Норма достигнута! 🎉' if today_ml >= norm else f'До нормы: {norm - today_ml} мл'}\n\n"
        f"💡 Норма: 30–35 мл на 1 кг веса\nДобавь:",
        reply_markup=water_kb()
    )

@router.callback_query(F.data.startswith("water_"))
async def add_water(callback: CallbackQuery):
    uid = callback.from_user.id
    ml = int(callback.data.replace("water_", ""))
    db.add_water(uid, ml)
    today_ml = db.get_today_water(uid)
    norm = 2500
    pct = min(100, int(today_ml / norm * 100))
    bar_filled = min(20, int(pct / 5))
    bar = "💧" * bar_filled + "░" * (20 - bar_filled)
    await callback.message.edit_text(
        f"💧 ТРЕКЕР ВОДЫ\n━━━━━━━━━━━━━━━━━━━━\n"
        f"[{bar}]\n"
        f"Сегодня: {today_ml} мл / {norm} мл ({pct}%)\n\n"
        f"{'✅ Норма достигнута! 🎉' if today_ml >= norm else f'До нормы: {norm - today_ml} мл'}\n\n"
        f"Добавить ещё:",
        reply_markup=water_kb()
    )
    await callback.answer(f"+{ml} мл 💧")

# ╔══════════════════════════════════════╗
#              ЗАМЕРЫ ТЕЛА
# ╚══════════════════════════════════════╝
@router.message(F.text == "📐 Замеры")
async def measurements_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    history = db.get_measurements(uid, limit=3)
    lines = ["📐 ЗАМЕРЫ ТЕЛА\n━━━━━━━━━━━━━━━━━━━━"]
    if history:
        latest = history[0]
        lines.append("📊 Последние замеры:")
        for field, label in [('chest','Грудь'),('waist','Талия'),('hips','Бёдра'),('bicep','Бицепс')]:
            if latest.get(field):
                lines.append(f"  {label}: {latest[field]} см")
        lines.append(f"  📅 {latest['created_at'][:10]}")
        if len(history) >= 2:
            prev = history[1]
            lines.append("\n📈 Изменения vs. прошлый раз:")
            for field, label in [('chest','Грудь'),('waist','Талия'),('hips','Бёдра')]:
                if latest.get(field) and prev.get(field):
                    diff = round(latest[field] - prev[field], 1)
                    sign = "+" if diff > 0 else ""
                    lines.append(f"  {label}: {sign}{diff} см")
    else:
        lines.append("Замеров пока нет.")
    lines += ["", "Добавить замеры: /measure"]
    await message.answer("\n".join(lines))

@router.message(Command("measure"))
async def start_measure(message: Message, state: FSMContext):
    if not await check_access(message): return
    await state.set_state(MeasureFSM.chest)
    await message.answer("📐 НОВЫЕ ЗАМЕРЫ\n\nШаг 1/4 — Обхват груди (см):\nПример: 100\n\nЕсли не хочешь вводить — напиши 0")

@router.message(MeasureFSM.chest)
async def measure_chest(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(',','.'))
    except:
        return await message.answer("❌ Введи число:")
    await state.update_data(chest=val if val > 0 else None)
    await state.set_state(MeasureFSM.waist)
    await message.answer("Шаг 2/4 — Обхват талии (см):")

@router.message(MeasureFSM.waist)
async def measure_waist(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(',','.'))
    except:
        return await message.answer("❌ Введи число:")
    await state.update_data(waist=val if val > 0 else None)
    await state.set_state(MeasureFSM.hips)
    await message.answer("Шаг 3/4 — Обхват бёдер (см):")

@router.message(MeasureFSM.hips)
async def measure_hips(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(',','.'))
    except:
        return await message.answer("❌ Введи число:")
    await state.update_data(hips=val if val > 0 else None)
    await state.set_state(MeasureFSM.bicep)
    await message.answer("Шаг 4/4 — Обхват бицепса (см):")

@router.message(MeasureFSM.bicep)
async def measure_bicep(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(',','.'))
    except:
        return await message.answer("❌ Введи число:")
    data = await state.get_data()
    data['bicep'] = val if val > 0 else None
    await state.clear()
    db.add_measurement(message.from_user.id, **data)
    lines = ["✅ ЗАМЕРЫ СОХРАНЕНЫ!\n━━━━━━━━━━━━━━━━━━━━"]
    for field, label in [('chest','Грудь'),('waist','Талия'),('hips','Бёдра'),('bicep','Бицепс')]:
        if data.get(field):
            lines.append(f"📏 {label}: {data[field]} см")
    await message.answer("\n".join(lines))

# ╔══════════════════════════════════════╗
#              РЕФЕРАЛЬНАЯ СИСТЕМА
# ╚══════════════════════════════════════╝
@router.message(F.text == "🔗 Реферал")
async def referral_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    count = db.get_referral_count(uid)
    bonus = db.get_referral_bonus_days(uid)
    bonus_per_ref = int(db.get_setting("referral_bonus_days", "7"))
    import os
    bot_username = os.getenv("BOT_USERNAME", "your_bot")
    ref_link = f"https://t.me/{bot_username}?start=ref{uid}"
    await message.answer(
        f"🔗 РЕФЕРАЛЬНАЯ ПРОГРАММА\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Приглашай друзей и получай БЕСПЛАТНЫЕ дни подписки!\n\n"
        f"📊 Твоя статистика:\n"
        f"👥 Приглашено: {count} чел.\n"
        f"🎁 Заработано: {bonus} дней\n\n"
        f"💰 За каждого друга, который оформит подписку:\n"
        f"   → ты получаешь +{bonus_per_ref} дней Premium!\n\n"
        f"🔗 Твоя ссылка:\n{ref_link}\n\n"
        f"📤 Поделись с друзьями!"
    )

# ╔══════════════════════════════════════╗
#                 ПРОГРЕСС
# ╚══════════════════════════════════════╝
@router.message(F.text == "📊 Прогресс")
async def progress_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    streak = db.get_workout_streak(uid)
    streak_text = f"🔥 Стрик: {streak} дней подряд!" if streak > 0 else ""
    await message.answer(
        f"📊 МОЙ ПРОГРЕСС\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{streak_text}\n\n"
        f"⚖️ /weight 75.5 — записать вес\n"
        f"🏋️ /workout Ноги — записать тренировку\n"
        f"🍽 /cal 2200 — записать калории\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 /history | 🏋️ /workouts | 📈 /calhistory"
    )

@router.message(Command("weight"))
async def log_weight(message: Message):
    if not await check_access(message): return
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return await message.answer("⚖️ /weight 75.5")
    try:
        w = float(args[1].replace(',','.'))
    except:
        return await message.answer("❌ Пример: /weight 75.5")
    uid = message.from_user.id
    db.add_weight(uid, w)
    history = db.get_weight_history(uid, limit=2)
    text = f"✅ Вес: {w} кг сохранён!\n"
    if len(history) >= 2:
        diff = round(history[0]['weight'] - history[1]['weight'], 1)
        text += f"{'📈' if diff>0 else '📉'} Изменение: {'+' if diff>0 else ''}{diff} кг"
    await message.answer(text)

@router.message(Command("history"))
async def weight_history(message: Message):
    if not await check_access(message): return
    history = db.get_weight_history(message.from_user.id, limit=10)
    if not history: return await message.answer("Нет записей. /weight 75")
    lines = ["📊 ИСТОРИЯ ВЕСА\n━━━━━━━━━━━━━━━━━━━━"]
    for i,r in enumerate(history):
        lines.append(f"{i+1}. {r['created_at'][:10]} — {r['weight']} кг")
    if len(history) >= 2:
        diff = round(history[0]['weight'] - history[-1]['weight'], 1)
        lines.append(f"\n{'📈' if diff>0 else '📉'} За период: {'+' if diff>0 else ''}{diff} кг")
    await message.answer("\n".join(lines))

@router.message(Command("workout"))
async def log_workout(message: Message):
    if not await check_access(message): return
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return await message.answer("🏋️ /workout Ноги")
    uid = message.from_user.id
    db.add_workout(uid, workout_type=args[1].strip())
    streak = db.get_workout_streak(uid)
    await message.answer(f"✅ Тренировка записана!\n🔥 Стрик: {streak} дн. | 🏆 Всего: {db.get_workout_count(uid)}")

@router.message(Command("workouts"))
async def workout_history(message: Message):
    if not await check_access(message): return
    history = db.get_workout_history(message.from_user.id, limit=10)
    if not history: return await message.answer("Нет тренировок. /workout Ноги")
    lines = ["🏋️ ИСТОРИЯ ТРЕНИРОВОК\n━━━━━━━━━━━━━━━━━━━━"]
    for i,r in enumerate(history):
        lines.append(f"{i+1}. {r['created_at'][:10]} — {r['workout_type']}")
    lines.append(f"\n🔥 Стрик: {db.get_workout_streak(message.from_user.id)} дн. | 🏆 Всего: {db.get_workout_count(message.from_user.id)}")
    await message.answer("\n".join(lines))

@router.message(Command("cal"))
async def log_calories(message: Message):
    if not await check_access(message): return
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return await message.answer("🍽 /cal 2200")
    try:
        cal = int(args[1])
    except:
        return await message.answer("❌ /cal 2200")
    db.add_calories(message.from_user.id, cal)
    await message.answer(f"✅ {cal} ккал записано!\n📊 Среднее: {db.get_avg_calories(message.from_user.id)}/день")

@router.message(Command("calhistory"))
async def cal_history(message: Message):
    if not await check_access(message): return
    history = db.get_calories_history(message.from_user.id, limit=7)
    if not history: return await message.answer("Нет записей. /cal 2200")
    lines = ["🍽 КАЛОРИИ ЗА НЕДЕЛЮ\n━━━━━━━━━━━━━━━━━━━━"]
    for i,r in enumerate(history):
        lines.append(f"{i+1}. {r['created_at'][:10]} — {r['calories']} ккал")
    lines.append(f"\n📊 Среднее: {db.get_avg_calories(message.from_user.id)}/день")
    await message.answer("\n".join(lines))

# ╔══════════════════════════════════════╗
#               СТАТИСТИКА
# ╚══════════════════════════════════════╝
@router.message(F.text == "📋 Статистика")
async def statistics(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    user = db.get_user(uid)
    stats = db.get_stats(uid)
    goal_names = {"gain":"💪 Набор","loss":"🔥 Похудение","maintain":"⚖️ Поддержание"}
    lines = [
        "📋 МОЯ СТАТИСТИКА\n━━━━━━━━━━━━━━━━━━━━",
        f"🎯 Цель: {goal_names.get(user.get('goal','maintain'),'—')}",
        f"⭐ Статус: {'Premium' if db.is_premium(uid) else 'Trial' if db.is_trial(uid) else 'Free'}",
        f"🔥 Стрик тренировок: {stats['streak']} дней",
    ]
    if stats['current_weight']:
        lines.append(f"⚖️ Текущий вес: {stats['current_weight']} кг")
    if stats['weight_change'] is not None:
        diff = stats['weight_change']
        lines.append(f"{'📈' if diff>0 else '📉'} Изменение веса: {'+' if diff>0 else ''}{diff} кг")
    lines += [
        f"🏋️ Тренировок всего: {stats['workouts_total']}",
        f"🍽 Среднее ккал: {stats['avg_calories'] or '—'}/день",
        f"💧 Вода сегодня: {stats['today_water']} мл",
        "\n━━━━━━━━━━━━━━━━━━━━",
        "/history | /workouts | /calhistory"
    ]
    await message.answer("\n".join(lines))

# ╔══════════════════════════════════════╗
#               НАПОМИНАНИЯ
# ╚══════════════════════════════════════╝
@router.message(F.text == "🔔 Напоминания")
async def notifications_menu(message: Message):
    if not await check_access(message): return
    uid = message.from_user.id
    notif = db.get_user(uid).get('notifications', 1)
    status = "✅ Включены" if notif else "❌ Выключены"
    toggle_cb = "notif_off" if notif else "notif_on"
    toggle_text = "Выключить" if notif else "Включить"
    await message.answer(
        f"🔔 НАПОМИНАНИЯ\n━━━━━━━━━━━━━━━━━━━━\n{status}\n\n"
        f"🌅 08:00 — утренняя мотивация\n🌙 20:00 — вечернее напоминание",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🔔 {toggle_text}", callback_data=toggle_cb)]
        ])
    )

@router.callback_query(F.data.in_(["notif_on","notif_off"]))
async def toggle_notifications(callback: CallbackQuery):
    val = 1 if callback.data == "notif_on" else 0
    db.update_user(callback.from_user.id, notifications=val)
    await callback.answer(f"{'✅ Включены' if val else '❌ Выключены'}")
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔔 {'Выключить' if val else 'Включить'}", callback_data=f"notif_{'off' if val else 'on'}")]
    ]))

# ╔══════════════════════════════════════╗
#                ПОДПИСКА
# ╚══════════════════════════════════════╝
@router.message(F.text.in_(["⭐ Подписка", "⭐ Купить подписку"]))
async def subscription_menu(message: Message):
    uid = message.from_user.id
    if db.is_banned(uid): return
    db.add_user(uid, message.from_user.username, message.from_user.first_name)
    is_prem = db.is_premium(uid)
    is_trial_active = db.is_trial(uid)
    days = db.days_left(uid)
    plans = get_plans()
    if is_prem:
        from datetime import datetime
        sub = db.get_subscription(uid)
        exp = datetime.fromisoformat(sub['expires_at'])
        await message.answer(
            f"⭐ PREMIUM АКТИВЕН ✅\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 До: {exp.strftime('%d.%m.%Y')} ({days} дн.)\n\n"
            f"Продлить подписку:",
            reply_markup=subscription_plans_kb()
        )
    else:
        trial_note = f"\n⚠️ Пробный период: {days} дн. осталось\n" if is_trial_active else ""
        await message.answer(
            f"⭐ FITNESS AI PREMIUM\n━━━━━━━━━━━━━━━━━━━━\n"
            f"{trial_note}\n"
            f"Полный доступ ко всем функциям:\n"
            f"🤖 AI тренер (OpenAI + Gemini + OpenRouter)\n"
            f"💪 Все планы тренировок и питания\n"
            f"📐 Замеры тела и BMI\n"
            f"💧 Трекер воды и калорий\n"
            f"🔗 Реферальная программа\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Оплата через Telegram Stars ⭐\n"
            f"1 Star ≈ 20₽  |  {plans['month']['stars']} Stars ≈ {plans['month']['stars']*20:,}₽/мес\n\n"
            f"Выбери план:",
            reply_markup=subscription_plans_kb()
        )

@router.callback_query(F.data == "sub_plans")
async def sub_plans_cb(callback: CallbackQuery):
    await callback.message.answer("⭐ FITNESS AI PREMIUM\n━━━━━━━━━━━━━━━━━━━━\nВыбери план:", reply_markup=subscription_plans_kb())
    await callback.answer()

@router.callback_query(F.data.in_(["buy_month","buy_3month","buy_year"]))
async def send_invoice_cb(callback: CallbackQuery):
    plans = get_plans()
    plan_key = callback.data.replace("buy_","")
    plan = plans[plan_key]
    await callback.message.answer_invoice(
        title=f"FITNESS AI Premium — {plan['label']}",
        description="🤖 AI тренер | 💪 Тренировки | 🍽 Питание | 📊 Трекинг",
        payload=f"premium_{plan_key}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"Premium {plan['label']}", amount=plan['stars'])],
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def payment_done(message: Message):
    plans = get_plans()
    payload = message.successful_payment.invoice_payload
    stars = message.successful_payment.total_amount
    uid = message.from_user.id
    payment_id = message.successful_payment.telegram_payment_charge_id
    plan_key = payload.replace("premium_","")
    plan = plans.get(plan_key, {"days":30,"label":"1 месяц"})
    expires = db.activate_premium(uid, days=plan["days"], stars=stars, payment_id=payment_id)
    is_admin = uid in ADMIN_IDS
    await message.answer(
        f"🎉 ОПЛАТА ПРОШЛА!\n━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ Premium до: {expires.strftime('%d.%m.%Y')}\n\n"
        f"🤖 Напиши 🤖 вопрос → AI тренер\n"
        f"📅 Программа → AI программа\n"
        f"🍽 Питание → AI план питания\n\n"
        f"Спасибо за поддержку! 💪",
        reply_markup=main_menu(is_admin)
    )

# ╔══════════════════════════════════════╗
#       РАСШИРЕННАЯ АДМИН-ПАНЕЛЬ
# ╚══════════════════════════════════════╝
def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика",        callback_data="adm_stats")],
        [InlineKeyboardButton(text="👥 Пользователи",      callback_data="adm_users"),
         InlineKeyboardButton(text="💰 Платежи",           callback_data="adm_payments")],
        [InlineKeyboardButton(text="⭐ Выдать Premium",    callback_data="adm_grant"),
         InlineKeyboardButton(text="❌ Отозвать Premium",  callback_data="adm_revoke")],
        [InlineKeyboardButton(text="🚫 Забанить",          callback_data="adm_ban"),
         InlineKeyboardButton(text="✅ Разбанить",         callback_data="adm_unban")],
        [InlineKeyboardButton(text="📢 Рассылка",          callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="✉️ Написать юзеру",   callback_data="adm_msg")],
        [InlineKeyboardButton(text="⚙️ Настройки бота",   callback_data="adm_settings")],
    ])

def admin_settings_kb(settings: dict):
    labels = {
        "trial_days":           "🎁 Пробный период (дни)",
        "price_month_stars":    "💰 Цена 1 мес (Stars)",
        "price_3month_stars":   "💰 Цена 3 мес (Stars)",
        "price_year_stars":     "💰 Цена 1 год (Stars)",
        "referral_bonus_days":  "🔗 Реферал бонус (дни)",
        "welcome_text":         "👋 Приветственный текст",
    }
    rows = []
    for k, label in labels.items():
        val = settings.get(k, "—")
        short = val[:20] + "…" if len(str(val)) > 20 else val
        rows.append([InlineKeyboardButton(text=f"{label}: {short}", callback_data=f"adm_set_{k}")])
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(F.text == "🔑 Админ")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    await message.answer("🔑 ПАНЕЛЬ АДМИНИСТРАТОРА\n━━━━━━━━━━━━━━━━━━━━", reply_markup=admin_main_kb())

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    await message.answer("🔑 ПАНЕЛЬ АДМИНИСТРАТОРА", reply_markup=admin_main_kb())

@router.callback_query(F.data == "adm_back")
async def admin_back(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.edit_text("🔑 ПАНЕЛЬ АДМИНИСТРАТОРА\n━━━━━━━━━━━━━━━━━━━━", reply_markup=admin_main_kb())
    await callback.answer()

@router.callback_query(F.data == "adm_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    total = db.get_total_users()
    premium = db.get_premium_users_count()
    trial = db.get_trial_users_count()
    new_today = db.get_new_users_today()
    revenue = db.get_revenue_stars()
    revenue_today = db.get_revenue_today()
    await callback.message.edit_text(
        f"📊 СТАТИСТИКА БОТА\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всего пользователей: {total}\n"
        f"🆕 Новых сегодня: {new_today}\n"
        f"⭐ Premium: {premium}\n"
        f"🎁 Trial: {trial}\n"
        f"📊 Конверсия: {round(premium/total*100, 1) if total else 0}%\n\n"
        f"💰 ДОХОДЫ\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ Всего Stars: {revenue}\n"
        f"⭐ Сегодня Stars: {revenue_today}\n"
        f"💵 Всего ≈ {revenue*20:,} ₽\n"
        f"💵 Сегодня ≈ {revenue_today*20:,} ₽",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back")]])
    )
    await callback.answer()

@router.callback_query(F.data == "adm_users")
async def admin_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    users = db.get_all_users()
    lines = [f"👥 ПОЛЬЗОВАТЕЛИ ({len(users)})\n━━━━━━━━━━━━━━━━━━━━"]
    for u in users[:25]:
        uname = f"@{u['username']}" if u.get('username') else u.get('first_name','—')
        flags = ""
        if db.is_premium(u['user_id']): flags += "⭐"
        elif db.is_trial(u['user_id']): flags += "🎁"
        if u.get('is_banned'): flags += "🚫"
        goal_e = {"gain":"💪","loss":"🔥","maintain":"⚖️"}.get(u.get('goal',''),'')
        lines.append(f"`{u['user_id']}` {uname} {flags}{goal_e} | {u.get('joined_at','')[:10]}")
    if len(users) > 25:
        lines.append(f"…ещё {len(users)-25}")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back")]]),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "adm_payments")
async def admin_payments(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    payments = db.get_all_payments(limit=15)
    if not payments:
        await callback.message.edit_text("💰 Платежей пока нет.", reply_markup=admin_main_kb())
        return
    lines = [f"💰 ПОСЛЕДНИЕ ПЛАТЕЖИ ({len(payments)})\n━━━━━━━━━━━━━━━━━━━━"]
    for p in payments:
        uname = f"@{p['username']}" if p.get('username') else p.get('first_name') or f"ID:{p['user_id']}"
        lines.append(f"{p['created_at'][:10]} | {uname} | {p['stars']} ⭐ ≈{p['stars']*20}₽")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back")]])
    )
    await callback.answer()

@router.callback_query(F.data == "adm_settings")
async def admin_settings_view(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    settings = db.get_all_settings()
    await callback.message.edit_text(
        "⚙️ НАСТРОЙКИ БОТА\n━━━━━━━━━━━━━━━━━━━━\nНажми на параметр чтобы изменить:",
        reply_markup=admin_settings_kb(settings)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("adm_set_"))
async def admin_set_param_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    key = callback.data.replace("adm_set_","")
    current = db.get_setting(key)
    labels = {
        "trial_days": "пробный период (дни)",
        "price_month_stars": "цену 1 месяца (Stars)",
        "price_3month_stars": "цену 3 месяцев (Stars)",
        "price_year_stars": "цену 1 года (Stars)",
        "referral_bonus_days": "реферальный бонус (дни)",
        "welcome_text": "приветственный текст",
    }
    await state.update_data(setting_key=key)
    await state.set_state(AdminFSM.set_value)
    await callback.message.answer(
        f"⚙️ Изменить {labels.get(key, key)}\n"
        f"Текущее значение: {current}\n\n"
        f"Введи новое значение:"
    )
    await callback.answer()

@router.message(AdminFSM.set_value)
async def admin_set_param_value(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    data = await state.get_data()
    key = data.get('setting_key')
    await state.clear()
    db.set_setting(key, message.text.strip())
    await message.answer(f"✅ Настройка '{key}' обновлена:\n{message.text.strip()}")

# ── Рассылка ──────────────────────────────────────────────
@router.callback_query(F.data == "adm_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.broadcast)
    await callback.message.answer(
        "📢 РАССЫЛКА\n\nВведи текст рассылки.\n"
        "Поддерживается разметка: *жирный*, _курсив_\n\n"
        "Отмена: /cancel"
    )
    await callback.answer()

@router.message(AdminFSM.broadcast)
async def admin_do_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    text = message.text
    await state.clear()
    users = db.get_users_with_notifications()
    await message.answer(f"⏳ Рассылка для {len(users)} пользователей...")
    sent = failed = 0
    for uid in users:
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except:
            failed += 1
    await message.answer(f"✅ Рассылка завершена!\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}")

# ── Написать конкретному юзеру ─────────────────────────────
@router.callback_query(F.data == "adm_msg")
async def admin_msg_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.msg_uid)
    await callback.message.answer("✉️ Введи user_id пользователя:")
    await callback.answer()

@router.message(AdminFSM.msg_uid)
async def admin_msg_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.strip())
    except:
        return await message.answer("❌ Неверный ID")
    await state.update_data(target_uid=uid)
    await state.set_state(AdminFSM.msg_text)
    user = db.get_user(uid)
    uname = f"@{user.get('username')}" if user.get('username') else user.get('first_name','—')
    await message.answer(f"📨 Пишешь пользователю {uname} ({uid})\nВведи текст сообщения:")

@router.message(AdminFSM.msg_text)
async def admin_msg_send(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    data = await state.get_data()
    uid = data.get('target_uid')
    await state.clear()
    try:
        await message.bot.send_message(uid, f"💬 Сообщение от администратора:\n\n{message.text}")
        await message.answer(f"✅ Сообщение отправлено пользователю {uid}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ── Выдать/Отозвать Premium ────────────────────────────────
@router.callback_query(F.data == "adm_grant")
async def admin_grant_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.grant_uid)
    await callback.message.answer("⭐ Введи user_id для выдачи Premium:")
    await callback.answer()

@router.message(AdminFSM.grant_uid)
async def admin_grant_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.strip())
    except:
        return await message.answer("❌ Неверный ID")
    await state.update_data(grant_uid=uid)
    await state.set_state(AdminFSM.grant_days)
    await message.answer("На сколько дней? (например: 30)")

@router.message(AdminFSM.grant_days)
async def admin_do_grant(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        days = int(message.text.strip())
    except:
        return await message.answer("❌ Введи число дней:")
    data = await state.get_data()
    uid = data.get('grant_uid')
    await state.clear()
    expires = db.grant_premium(uid, days)
    await message.answer(f"✅ Premium на {days} дней выдан пользователю {uid}\nДо: {expires.strftime('%d.%m.%Y')}")
    try:
        await message.bot.send_message(uid, f"🎁 Тебе выдан Premium на {days} дней!\nДо: {expires.strftime('%d.%m.%Y')} 💪")
    except:
        pass

@router.callback_query(F.data == "adm_revoke")
async def admin_revoke_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.revoke_uid)
    await callback.message.answer("❌ Введи user_id для отзыва Premium:")
    await callback.answer()

@router.message(AdminFSM.revoke_uid)
async def admin_do_revoke(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.strip())
    except:
        return await message.answer("❌ Неверный ID")
    await state.clear()
    db.revoke_premium(uid)
    await message.answer(f"✅ Premium отозван у {uid}")

# ── Бан/Разбан ────────────────────────────────────────────
@router.callback_query(F.data == "adm_ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.ban_uid)
    await callback.message.answer("🚫 Введи user_id для бана:")
    await callback.answer()

@router.message(AdminFSM.ban_uid)
async def admin_do_ban(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.strip())
    except:
        return await message.answer("❌ Неверный ID")
    await state.clear()
    db.ban_user(uid)
    await message.answer(f"🚫 Пользователь {uid} заблокирован")

@router.callback_query(F.data == "adm_unban")
async def admin_unban_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return await callback.answer("❌")
    await state.set_state(AdminFSM.unban_uid)
    await callback.message.answer("✅ Введи user_id для разбана:")
    await callback.answer()

@router.message(AdminFSM.unban_uid)
async def admin_do_unban(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        uid = int(message.text.strip())
    except:
        return await message.answer("❌ Неверный ID")
    await state.clear()
    db.unban_user(uid)
    await message.answer(f"✅ Пользователь {uid} разблокирован")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Отменено.")

# ╔══════════════════════════════════════╗
#                REGISTER
# ╚══════════════════════════════════════╝
def register_all_handlers(dp):
    dp.include_router(router)
