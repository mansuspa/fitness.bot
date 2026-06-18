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

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="💪 Масса")],
        [KeyboardButton(text="⚖️ Поддержание")],
        [KeyboardButton(text="🍽 Питание"), KeyboardButton(text="🏋️ Тренировки")],
        [KeyboardButton(text="📊 Моя форма"), KeyboardButton(text="📈 Прогресс")]
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
        f"💪 Привет, {username}!\n\nЯ твой фитнес-тренер.\nВыбери цель 👇",
        reply_markup=menu
    )

# ---------------- GOALS ----------------

@router.message(F.text == "🔥 Похудение")
async def loss(message: Message):
    db.update_user(message.from_user.id, goal="loss")
    await message.answer("🔥 Цель установлена: ПОХУДЕНИЕ")

@router.message(F.text == "💪 Масса")
async def gain(message: Message):
    db.update_user(message.from_user.id, goal="gain")
    await message.answer("💪 Цель установлена: МАССА")

@router.message(F.text == "⚖️ Поддержание")
async def maintain(message: Message):
    db.update_user(message.from_user.id, goal="maintain")
    await message.answer("⚖️ Цель установлена: ПОДДЕРЖАНИЕ")

# ---------------- CALORIES ----------------

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

# ---------------- TRAINING ----------------

@router.message(F.text == "🏋️ Тренировки")
async def training(message: Message):
    user = db.get_user(message.from_user.id)
    goal = user.get("goal", "maintain")

    plan = workout.get_workout_plan(goal)

    text = f"🏋️ {plan['title']}\n\n"

    for day, desc in plan["days"].items():
        text += f"{day}: {desc}\n"

    text += "\n💪 УПРАЖНЕНИЯ:\n"

    for group, exs in plan["exercises"].items():
        text += f"\n{group}:\n"
        for ex in exs:
            text += f"• {ex}\n"

    await message.answer(text)

# ---------------- FOOD ----------------

@router.message(F.text == "🍽 Питание")
async def food(message: Message):
    user = db.get_user(message.from_user.id)
    goal = user.get("goal", "maintain")

    guide = nutrition.food_guide()
    data = guide[goal]

    text = f"{data['title']}\n\n🍽 ЕДА:\n"

    for item in data["eat"]:
        text += f"• {item}\n"

    if "avoid" in data:
        text += "\n❌ ИЗБЕГАТЬ:\n"
        for item in data["avoid"]:
            text += f"• {item}\n"

    if "add_tip" in data:
        text += f"\n💡 {data['add_tip']}"

    if "tip" in data:
        text += f"\n💡 {data['tip']}"

    await message.answer(text)

# ---------------- PROGRESS ----------------

@router.message(F.text == "📈 Прогресс")
async def progress(message: Message):
    user = db.get_user(message.from_user.id)

    history = user.get("weight_history", [])

    if len(history) < 2:
        await message.answer("📊 Пока нет данных")
        return

    diff = history[-1] - history[0]

    await message.answer(
        f"📈 ПРОГРЕСС\n\n"
        f"Старт: {history[0]} кг\n"
        f"Сейчас: {history[-1]} кг\n"
        f"Изменение: {diff:+.1f} кг"
    )

# ---------------- WEIGHT INPUT ----------------

@router.message(F.text.regexp(r"^\d{2,3}$"))
async def weight(message: Message):
    db.add_weight(message.from_user.id, int(message.text))
    await message.answer("⚖️ Вес сохранён")

# ---------------- FALLBACK ----------------

@router.message()
async def fallback(message: Message):
    await message.answer("Выбери кнопку 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)