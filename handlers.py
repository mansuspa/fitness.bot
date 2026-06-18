import logging

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

from database import Database
from nutrition import Nutrition
from workout import Workout

router = Router()

db = Database()
nutrition = Nutrition()
workout = Workout()

# ---------------- UI ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="💪 Масса")],
        [KeyboardButton(text="⚖️ Поддержание")],
        [KeyboardButton(text="📊 Моя форма"), KeyboardButton(text="🏋️ Тренировки")],
        [KeyboardButton(text="📈 Прогресс")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    db.add_user(user_id, username)

    await message.answer(
        f"💪 Привет, {username}!\n\n"
        f"Я твой AI фитнес-тренер.\n"
        f"Выбери цель ниже 👇",
        reply_markup=menu
    )

# ---------------- ЦЕЛИ ----------------

@router.message(F.text == "🔥 Похудение")
async def loss(message: Message):
    db.update_user(message.from_user.id, goal="loss")
    await message.answer("🔥 Цель: ПОХУДЕНИЕ установлена")

@router.message(F.text == "💪 Масса")
async def gain(message: Message):
    db.update_user(message.from_user.id, goal="gain")
    await message.answer("💪 Цель: НАБОР МАССЫ установлен")

@router.message(F.text == "⚖️ Поддержание")
async def maintain(message: Message):
    db.update_user(message.from_user.id, goal="maintain")
    await message.answer("⚖️ Цель: ПОДДЕРЖАНИЕ установлено")

# ---------------- ФОРМА ----------------

@router.message(F.text == "📊 Моя форма")
async def form(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("Сначала /start")
        return

    data = nutrition.calculate_calories(
        user["weight"],
        user["height"],
        user["age"],
        user["gender"],
        user["goal"]
    )

    await message.answer(
        f"📊 ТВОЯ ФОРМА\n\n"
        f"🔥 Калории: {data['calories']}\n"
        f"🥩 Белки: {data['protein']} г\n"
        f"🥑 Жиры: {data['fats']} г\n"
        f"🍞 Углеводы: {data['carbs']} г\n"
        f"⚡ TDEE: {data['tdee']}"
    )

# ---------------- ТРЕНИРОВКИ ----------------

@router.message(F.text == "🏋️ Тренировки")
async def training(message: Message):
    user = db.get_user(message.from_user.id)

    goal = user.get("goal", "maintain")

    plan = workout.get_workout_plan(goal)

    text = f"🏋️ {plan['title']}\n\n"

    for day, desc in plan["days"].items():
        text += f"{day}: {desc}\n"

    text += "\n💪 Упражнения:\n"

    for group, exs in plan["exercises"].items():
        text += f"\n{group}:\n"
        for ex in exs:
            text += f"• {ex}\n"

    await message.answer(text)

# ---------------- ПРОГРЕСС ----------------

@router.message(F.text == "📈 Прогресс")
async def progress(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("Сначала /start")
        return

    history = user.get("weight_history", [])

    if len(history) < 2:
        await message.answer("📊 Пока мало данных для прогресса")
        return

    start = history[0]
    current = history[-1]
    diff = current - start

    trend = "📉 похудение" if diff < 0 else "📈 набор"

    await message.answer(
        f"📈 ПРОГРЕСС\n\n"
        f"Старт: {start} кг\n"
        f"Сейчас: {current} кг\n"
        f"Изменение: {diff:+.1f} кг\n"
        f"Тренд: {trend}"
    )

# ---------------- ВЕС ----------------

@router.message(F.text.regexp(r"^\d{2,3}$"))
async def weight_input(message: Message):
    weight = int(message.text)

    db.add_weight(message.from_user.id, weight)

    await message.answer(
        f"⚖️ Вес сохранён: {weight} кг\n\n"
        f"📊 Напиши 'Прогресс' чтобы увидеть динамику"
    )

# ---------------- FALLBACK ----------------

@router.message()
async def fallback(message: Message):
    await message.answer("Выбери действие из меню 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)