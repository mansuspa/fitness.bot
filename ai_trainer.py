
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fitness_ai(user_goal: str, user_message: str):
    system_prompt = f"""
Ты профессиональный фитнес-тренер уровня PRO.

Задача:
- помогать в тренировках
- объяснять технику упражнений
- составлять питание (в граммах)
- помогать худеть и набирать массу

Всегда:
- пиши по-русски
- давай конкретику
- используй цифры (повторы, подходы, граммы)
- не пиши воду

ЦЕЛЬ ПОЛЬЗОВАТЕЛЯ: {user_goal}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content