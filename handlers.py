import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from database import Database
from nutrition import Nutrition
from workout import Workout

logger = logging.getLogger(__name__)
router = Router()

# Инициализация модулей
db = Database()
nutrition = Nutrition()
workout = Workout()

@router.message(Command("help"))
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    # Сохранение пользователя в базе данных
    db.add_user(user_id, username)
    
    await message.answer(
        f"👋 Привет, {username}!\n\n"
        f"Я твой фитнес-помощник.\n\n"
        f"Выбери команду в меню или напиши /help для справки."
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    help_text = """📚 **Команды бота:**

/start - Начать работу
/help - Справка
/menu - Главное меню

/food - 🍽️ Питание
/workout - 💪 Тренировки
/profile - 👤 Мой профиль
/settings - ⚙️ Настройки
"""
    await message.answer(help_text)

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Главное меню"""
    menu_text = """🍽️ **Главное меню**

Выберите раздел:

/food - 🍽️ Питание
/workout - 💪 Тренировки
/profile - 👤 Мой профиль
/settings - ⚙️ Настройки
"""
    await message.answer(menu_text)

@router.message(Command("food"))
async def cmd_food(message: Message):
    """Модуль питания"""
    await message.answer(
        "🍽️ **Модуль питания**\n\n"
        "Рассчитаю твои калории и составлю рацион.\n\n"
        "Напиши свой вес, рост и возраст, и я помогу!"
    )

@router.message(Command("workout"))
async def cmd_workout(message: Message):
    """Модуль тренировок"""
    await message.answer(
        "💪 **Модуль тренировок**\n\n"
        "Дам рекомендации по тренировкам и упражнениям.\n\n"
        "Напиши, какую группу мышц хочешь тренировать."
    )

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Профиль пользователя"""
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    if user_data:
        profile_text = f"👤 **Твой профиль**\n\n"
        profile_text += f"ID: `{user_id}`\n"
        profile_text += f"Имя: {user_data['username']}\n"
        profile_text += f"Дата регистрации: {user_data['created_at']}\n"
        
        await message.answer(profile_text)
    else:
        await message.answer("Профиль не найден. Напиши /start")

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Настройки"""
    await message.answer(
        "⚙️ **Настройки**\n\n"
        "Здесь будут настройки бота."
    )

@router.message(Command("unknown"))
async def cmd_unknown(message: Message):
    """Обработка неизвестных команд"""
    await message.answer(
        "Я не понимаю эту команду. Напиши /help для справки."
    )

def register_all_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.include_router(router)
    logger.info("Все обработчики зарегистрированы")