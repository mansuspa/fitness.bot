from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database import Database
from nutrition import Nutrition
from workout import Workout
from ai_trainer import fitness_ai

router = Router()

db = Database()
nut = Nutrition()
work = Workout()

# ---------------- MENU ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💪 Набор массы"), KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Поддержание")],

        [KeyboardButton(text="🏋️ Тренировки")],
        [KeyboardButton(text="🍽 Питание")],
        [KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="🧠 SMART режим")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------
@router.message(CommandStart())
async def start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "💪 FITNESS AI V7 PRO\n\nВыбери цель:",
        reply_markup=menu
    )

# ---------------- GOALS ----------------
@router.message(F.text.in_(["💪 Набор массы", "🔥 Похудение", "⚖️ Поддержание"]))
async def set_goal(message: Message):

    goals = {
        "💪 Набор массы": "gain",
        "🔥 Похудение": "loss",
        "⚖️ Поддержание": "maintain"
    }

    db.update_user(message.from_user.id, goal=goals.get(message.text, "maintain"))

    await message.answer("✅ цель установлена")

# ---------------- TRAINING ----------------
@router.message(F.text == "🏋️ Тренировки")
async def training(message: Message):

    user = db.get_user(message.from_user.id)
    if not user:
        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    plan = work.get_workout_plan(goal)

    text = f"{plan['title']}\n\n📅 РАСПИСАНИЕ:\n"

    for k, v in plan["schedule"].items():
        text += f"• {k}: {v}\n"

    text += "\n💪 ТРЕНИРОВКИ:\n"

    for group, items in plan["workouts"].items():
        text += f"\n🔹 {group.upper()}\n"

        for w in items:
            text += f"\n🏋️ {w['name']}\n"

            for ex in w["exercises"]:
                text += f"• {ex}\n"

    await message.answer(text)

# ---------------- FOOD (УМНОЕ ПИТАНИЕ) ----------------
@router.message(F.text == "🍽 Питание")
async def food(message: Message):

    user = db.get_user(message.from_user.id)
    if not user:
        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    plan = nut.get_nutrition_plan(goal)

    text = f"{plan['title']}\n\n📊 МАКРОСЫ:\n"

    for k, v in plan["macros"].items():
        text += f"• {k}: {v}\n"

    text += "\n🍽 ПИТАНИЕ:\n"

    for meal, items in plan["meals"].items():
        text += f"\n{meal.upper()}:\n"
        for i in items:
            text += f"• {i}\n"

    await message.answer(text)

# ---------------- PROGRESS ----------------
@router.message(F.text == "📊 Прогресс")
async def progress(message: Message):

    user = db.get_user(message.from_user.id)
    if not user:
        return await message.answer("нажми /start")

    text = "📊 ТВОЙ ПРОГРЕСС\n\n"

    text += f"🎯 цель: {user.get('goal', 'не задана')}\n"
    text += f"⚖️ вес: {user.get('weight', 'не указан')}\n"
    text += f"📏 рост: {user.get('height', 'не указан')}\n"
    text += f"🎂 возраст: {user.get('age', 'не указан')}\n"

    await message.answer(text)

# ---------------- SMART ----------------
@router.message(F.text == "🧠 SMART режим")
async def smart(message: Message):

    user = db.get_user(message.from_user.id)
    if not user:
        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    advice = {
        "gain": "💪 профицит + силовые 4-5 раз/нед",
        "loss": "🔥 дефицит + кардио + контроль еды",
        "maintain": "⚖️ баланс + 3 тренировки"
    }

    await message.answer(
        "🧠 SMART AI\n\n"
        f"🎯 цель: {goal}\n"
        f"📌 {advice[goal]}"
    )



# ---------------- 🤖 AI TRAINER ----------------

@router.message(F.text.startswith("🤖"))

async def ai_trainer(message: Message):

def register_all_handlers(dp):
    dp.include_router(router)

    user = db.get_user(message.from_user.id)

    if not user:

        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    text = message.text.replace("🤖", "").strip()

    if not text:

        return await message.answer("Напиши вопрос после 🤖")

    answer = fitness_ai(goal, text)

    await message.answer(answer)

# ---------------- FALLBACK ----------------
@router.message()
async def fallback(message: Message):
    await message.answer("выбери кнопку 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)