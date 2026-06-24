import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DB_FILE = os.getenv("DB_FILE", "fitness.db")

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "260182231").split(",") if x.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения")

TRAINING_PLANS = {
    "mass": {
        "monday": "PUSH — Грудь, Плечи, Трицепс",
        "tuesday": "PULL — Спина, Бицепс",
        "wednesday": "LEGS — Ноги",
        "thursday": "Отдых / Кардио",
        "friday": "PUSH — Повтор",
        "saturday": "PULL — Повтор",
        "sunday": "Отдых",
    },
    "fat_loss": {
        "monday": "Силовая + Кардио",
        "tuesday": "HIIT",
        "wednesday": "Силовая",
        "thursday": "Кардио",
        "friday": "Силовая + Кардио",
        "saturday": "Активный отдых",
        "sunday": "Отдых",
    }
}

NUTRITION = {
    "mass": {
        "breakfast": "Овсянка, 3 яйца, банан",
        "lunch": "Рис, куриное филе, овощи",
        "dinner": "Рыба, гречка, салат",
        "snack": "Творог, орехи, протеин",
        "protein_daily": "2.0–2.2 г/кг",
    },
    "fat_loss": {
        "breakfast": "Яичница, овсянка, яблоко",
        "lunch": "Куриная грудка, гречка, овощи",
        "dinner": "Рыба, овощи на пару",
        "snack": "Йогурт, огурец",
        "protein_daily": "2.2–2.4 г/кг",
    }
}
