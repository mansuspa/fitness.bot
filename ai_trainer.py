from openai import OpenAI

client = OpenAI(api_key="ТВОЙ_API_KEY")

def fitness_ai(goal, text):
    prompt = f"""
Ты фитнес тренер.

Цель: {goal}

Вопрос: {text}

Отвечай как тренер:
- упражнения
- техника
- ошибки
- коротко
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content