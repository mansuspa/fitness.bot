import logging

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command

from database import Database
from nutrition import Nutrition
from workout import Workout

logger = logging.getLogger(__name__)

router = Router()

db = Database()
nutrition = Nutrition()
workout = Workout()

# ---------------- КЛАВИАТУРА ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="💪 Масса")],
        [KeyboardButton(text="⚖️ Поддержание")],
        [KeyboardButton(text="🍽 Питание"), KeyboardButton(text="🏋️ Тренировки")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"

    db.add_user(user_id, username)

    await message.answer(
        f"💪 Добро пожаловать, {username}!\n\n"
        f"Я твой фитнес-ассистент.\n"
        f"Выбери цель ниже 👇",
        reply_markup=menu
    )

# ---------------- ЦЕЛИ ----------------

@router.message(F.text == "🔥 Похудение")
async def loss(message: Message):
    user_id = message.from_user.id
    db.update_user(user_id, goal="loss")

    plan = nutrition.get_nutrition_plan("loss")

    await message.answer(
        f"{plan['title']}\n\n"
        f"🍽 Белки: {plan['macros']['protein']}\n"
        f"🍞 Углеводы: {plan['macros']['carbs']}\n"
        f"🥑 Жиры: {plan['macros']['fats']}\n\n"
        f"Пример питания:\n"
        f"Завтрак: {plan['meals']['breakfast']}\n"
        f"Обед: {plan['meals']['lunch']}\n"
        f"Ужин: {plan['meals']['dinner']}",
        reply_markup=menu
    )

@router.message(F.text == "💪 Масса")
async def gain(message: Message):
    user_id = message.from_user.id
    db.update_user(user_id, goal="gain")

    plan = nutrition.get_nutrition_plan("gain")

    await message.answer(
        f"{plan['title']}\n\n"
        f"🍽 Белки: {plan['macros']['protein']}\n"
        f"🍞 Углеводы: {plan['macros']['carbs']}\n"
        f"🥑 Жиры: {plan['macros']['fats']}",
        reply_markup=menu
    )

@router.message(F.text == "⚖️ Поддержание")
async def maintain(message: Message):
    user_id = message.from_user.id
    db.update_user(user_id, goal="maintain")

    plan = nutrition.get_nutrition_plan("maintain")

    await message.answer(
        f"{plan['title']}\n\n"
        f"🍽 Питание:\n"
        f"Завтрак: {plan['meals']['breakfast']}\n"
        f"Обед: {plan['meals']['lunch']}\n"
        f"Ужин: {plan['meals']['dinner']}",
        reply_markup=menu
    )

# ---------------- ПИТАНИЕ ----------------

@router.message(F.text == "🍽 Питание")
async def food(message: Message):
    await message.answer(
        "🍽 Выбери цель сначала:\n\n"
        "🔥 Похудение\n💪 Масса\n⚖️ Поддержание"
    )

# ---------------- ТРЕНИРОВКИ ----------------

@router.message(F.text == "🏋️ Тренировки")
async def training(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)

    goal = user.get("goal") if user else "maintain"

    plan = workout.get_workout_plan(goal)

    text = f"🏋️ {plan['title']}\n\n"

    for day, desc in plan["days"].items():
        text += f"{day}: {desc}\n"

    text += "\n💪 Пример упражнений:\n"

    for group, exercises in plan["exercises"].items():
        text += f"\n{group}:\n"
        for ex in exercises:
            text += f"- {ex}\n"

    await message.answer(text, reply_markup=menu)

# ---------------- ПРОФИЛЬ ----------------

@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)

    if not user:
        await message.answer("Сначала нажми /start")
        return

    await message.answer(
        f"👤 Профиль\n\n"
        f"Имя: {user.get('username')}\n"
        f"Цель: {user.get('goal', 'не выбрана')}\n"
        f"Вес: {user.get('weight', '-')}\n"
        f"Рост: {user.get('height', '-')}\n"
        f"Возраст: {user.get('age', '-')}"
    )

# ---------------- ПОМОЩЬ ----------------

@router.message(F.text == "❓ Помощь")
async def help(message: Message):
    await message.answer(
        "💪 Фитнес бот:\n\n"
        "Выбирай цель → получай питание и тренировки\n"
        "🏋️ Тренировки — программа\n"
        "🍽 Питание — рацион\n"
        "👤 Профиль — данные"
    )

# ---------------- FALLBACK ----------------

@router.message()
async def fallback(message: Message):
    await message.answer("Выбери действие из меню 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)
    logger.info("V2 handlers loaded")