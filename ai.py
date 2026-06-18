from openai import OpenAI

client = OpenAI(api_key="ТВОЙ_API_KEY")

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