import os
from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")

print("OPENAI_API_KEY =", repr(key))
print(type(key))
print(len(key))
print(repr(key[:20]))

client = OpenAI(
    api_key=key
)

def fitness_ai(goal, text):

    prompt = f"""
Ты профессиональный фитнес тренер.

Цель пользователя: {goal}

Вопрос: {text}

Отвечай:
- упражнения
- техника
- питание
- ошибки
- коротко и по делу
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content