import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Настройка базы данных
DB_FILE = os.getenv("DB_FILE", "database.json")

# Настройка питания
MEALS_FILE = os.getenv("MEALS_FILE", "meals.json")

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения")