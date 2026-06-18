import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandHelp, Command
from database import Database
from nutrition import Nutrition
from workout import Workout

logger = logging.getLogger(__name__)
router = Router()

# Инициализация модулей
db = Database()
nutrition = Nutrition()
workout = Workout()

@router.message(CommandStart())
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

@router.message(CommandHelp())
async def cmd_help(message: Message):
    """Обработка команды /help"""
    help_text = """📚 **Команды бота:**

/start - Начать работу
/help - Справка
/menu - Главное меню

/food - 🍽️ Питание
/workout - 💪 Тренировки
/profile - 👤 Мой профиль
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
        "Напиши, какую цель преследуешь: набор или похудение."
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

@router.message(Command("food"))
async def cmd_food_calories(message: Message):
    """Расчёт калорий"""
    try:
        parts = message.text.split()
        if len(parts) < 4:
            await message.answer(
                "📊 **Расчёт калорий**\n\n"
                "Напиши: /food вес рост возраст\n\n"
                "Пример: /food 80 180 25"
            )
            return
        
        weight = float(parts[1])
        height = float(parts[2])
        age = int(parts[3])
        
        # Определяем пол по username
        username = message.from_user.username or ""
        gender = "male" if "male" in username.lower() or "m" in username.lower() else "female"
        
        # Расчёт калорий
        calories_data = nutrition.calculate_calories(weight, height, age, gender)
        
        text = f"📊 **Твой базовый обмен веществ:** {calories_data['bmr']} ккал\n\n"
        text += f"**Суточная норма:** {calories_data['daily_calories']} ккал\n\n"
        text += "Выбери цель:\n"
        text += "/food_gain - Набор массы\n"
        text += "/food_loss - Похудение"
        
        await message.answer(text)
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Напиши: /food вес рост возраст\n\n"
            "Пример: /food 80 180 25"
        )

@router.message(Command("food_gain"))
async def cmd_food_gain(message: Message):
    """План питания для набора"""
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    if user_data:
        weight = user_data.get('weight') or 70
        height = user_data.get('height') or 175
        age = user_data.get('age') or 25
        
        # Расчёт калорий
        calories_data = nutrition.calculate_calories(weight, height, age, "male")
        
        # Создание плана питания
        meal_plan = nutrition.create_meal_plan(calories_data['daily_calories'], "gain")
        
        text = nutrition.get_meal_plan_text(calories_data['daily_calories'], "gain")
        
        await message.answer(text)
    else:
        await message.answer("Сначала заполни профиль. Напиши /profile")

@router.message(Command("food_loss"))
async def cmd_food_loss(message: Message):
    """План питания для похудения"""
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    if user_data:
        weight = user_data.get('weight') or 70
        height = user_data.get('height') or 175
        age = user_data.get('age') or 25
        
        # Расчёт калорий
        calories_data = nutrition.calculate_calories(weight, height, age, "male")
        
        # Создание плана питания
        meal_plan = nutrition.create_meal_plan(calories_data['daily_calories'], "loss")
        
        text = nutrition.get_meal_plan_text(calories_data['daily_calories'], "loss")
        
        await message.answer(text)
    else:
        await message.answer("Сначала заполни профиль. Напиши /profile")

@router.message(Command("workout_gain"))
async def cmd_workout_gain(message: Message):
    """План тренировок для набора"""
    text = workout.get_workout_plan_text("gain")
    await message.answer(text)

@router.message(Command("workout_loss"))
async def cmd_workout_loss(message: Message):
    """План тренировок для похудения"""
    text = workout.get_workout_plan_text("loss")
    await message.answer(text)

@router.message()
async def cmd_unknown(message: Message):
    """Обработка неизвестных команд"""
    await message.answer(
        "Я не понимаю эту команду. Напиши /help для справки."
    )

def register_all_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.include_router(router)
    logger.info("Все обработчики зарегистрированы")