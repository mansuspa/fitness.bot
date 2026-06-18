import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in .env file")

# Database
DB_FILE = "users.json"

# Training Plans
TRAINING_PLANS = {
    "fat_loss": {
        "name": "🔥 ПОХУДЕНИЕ",
        "description": "Сжигание жира + мышечный тонус",
        "weekly_sessions": 4,
        "cardio_minutes": "25-35",
        "deficit": "500-700 ккал",
    },
    "mass": {
        "name": "💪 МАССА",
        "description": "Набор мышечной массы",
        "weekly_sessions": 4,
        "cardio_minutes": "0-10",
        "surplus": "300-500 ккал",
    }
}

# Nutrition Templates
NUTRITION = {
    "mass": {
        "breakfast": "🥚 Яйца (3-5 шт) + Овсянка",
        "lunch": "🍗 Курица (250g) + Рис (150g) + Овощи",
        "dinner": "🐟 Рыба (200g) + Сладкий картофель",
        "snack": "🥛 Творог (150g) + Ягоды",
        "protein_daily": "2.0 - 2.2g/kg"
    },
    "fat_loss": {
        "breakfast": "🥗 Овощи + Яйцо белки",
        "lunch": "🐟 Рыба (150g) + Салат",
        "dinner": "🍗 Курица (150g) + Броккoli",
        "snack": "🍎 Фрукт или Творог",
        "protein_daily": "1.8 - 2.0g/kg"
    }
}

# Premium Benefits
PREMIUM_BENEFITS = [
    "🎯 Персональный план на неделю",
    "📱 Отслеживание прогресса",
    "🤖 AI-рекомендации",
    "⚡ Быстрый расчет калорий",
    "📊 Подробная аналитика"
]