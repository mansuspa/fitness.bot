import os
from openai import OpenAI


print("OPENAI_API_KEY =", repr(os.getenv("OPENAI_API_KEY")))
print("OPENAI_PROJECT_ID =", repr(os.getenv("OPENAI_PROJECT_ID")))
print("OPENAI_ORG_ID =", repr(os.getenv("OPENAI_ORG_ID")))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
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