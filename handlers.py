from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database import Database
from nutrition import Nutrition
from workout import Workout

router = Router()

db = Database()
nut = Nutrition()
work = Workout()

# ---------------- MENU ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💪 Набор массы"), KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Поддержание")],
        [KeyboardButton(text="🏋️ Тренировки"), KeyboardButton(text="🍽 Питание")],
        [KeyboardButton(text="📊 Калории"), KeyboardButton(text="📈 Прогресс")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------
@router.message(CommandStart())
async def start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "💪 FITNESS APP V6\n\nВыбери цель:",
        reply_markup=menu
    )

# ---------------- GOALS ----------------
@router.message(F.text == "💪 Набор массы")
async def gain(message: Message):
    db.update(message.from_user.id, goal="gain")
    await message.answer("💪 цель: НАБОР МАССЫ")

@router.message(F.text == "🔥 Похудение")
async def loss(message: Message):
    db.update(message.from_user.id, goal="loss")
    await message.answer("🔥 цель: ПОХУДЕНИЕ")

@router.message(F.text == "⚖️ Поддержание")
async def maintain(message: Message):
    db.update(message.from_user.id, goal="maintain")
    await message.answer("⚖️ цель: ПОДДЕРЖАНИЕ")

# ---------------- TRAINING ----------------
@router.message(F.text == "🏋️ Тренировки")
async def training(message: Message):
    user = db.get_user(message.from_user.id)
    plan = work.plan(user["goal"])

    text = f"🏋️ {plan['title']}\n\n"

    text += "📅 ДНИ:\n"
    for d in plan["days"]:
        text += f"• {d}\n"

    text += "\n💪 УПРАЖНЕНИЯ:\n"
    for e in plan["exercises"]:
        text += f"• {e}\n"

    text += "\n🔥 СОВЕТ:\nНе жертвуй техникой ради веса"

    await message.answer(text)

# ---------------- FOOD ----------------
@router.message(F.text == "🍽 Питание")
async def food(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        return await message.answer("Нажми /start")

    goal = user.get("goal", "maintain")

    guide = nut.food(goal)

    data = guide.get(goal)

    if not data:
        data = guide["maintain"]

    text = f"{data['title']}\n\n🍽 ЕДА:\n"

    for item in data.get("eat", []):
        text += f"• {item}\n"

    if "avoid" in data:
        text += "\n❌ ИЗБЕГАТЬ:\n"
        for item in data["avoid"]:
            text += f"• {item}\n"

    if "tip" in data:
        text += f"\n💡 {data['tip']}"

    await message.answer(text)

# ---------------- CALORIES ----------------
@router.message(F.text == "📊 Калории")
async def calories(message: Message):
    user = db.get_user(message.from_user.id)

    cal = nut.calories(
        user["weight"],
        user["height"],
        user["age"],
        user["goal"]
    )

    await message.answer(
        f"🔥 калории: {cal['calories']}\n"
        f"🥩 белок: {cal['protein']}g\n"
        f"🥑 жиры: {cal['fat']}g\n"
        f"🍞 углеводы: {cal['carbs']}g"
    )

# ---------------- PROGRESS ----------------
@router.message(F.text == "📈 Прогресс")
async def progress(message: Message):
    user = db.get_user(message.from_user.id)

    await message.answer(
        f"👤 {user['username']}\n"
        f"🎯 цель: {user['goal']}\n"
        f"⚖️ вес: {user['weight']} кг\n"
        f"📏 рост: {user['height']} см"
    )

# ---------------- FALLBACK ----------------
@router.message()
async def fallback(message: Message):
    await message.answer("выбери кнопку 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)