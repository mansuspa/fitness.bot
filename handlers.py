from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database import Database
from ai import fitness_ai

router = Router()
db = Database()

# ================= MENU =================
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💪 Набор массы"), KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Поддержание")],

        [KeyboardButton(text="🏋️ Тренировки ЗАЛ"), KeyboardButton(text="🍽 Питание")],
        [KeyboardButton(text="🔥 Счётчик калорий"), KeyboardButton(text="🤖 AI тренер")]
    ],
    resize_keyboard=True
)

# ================= START =================
@router.message(CommandStart())
async def start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)

    await message.answer("💪 FITNESS AI V10", reply_markup=menu)

# ================= GOALS =================
@router.message(F.text.in_(["💪 Набор массы", "🔥 Похудение", "⚖️ Поддержание"]))
async def set_goal(message: Message):

    goals = {
        "💪 Набор массы": "gain",
        "🔥 Похудение": "loss",
        "⚖️ Поддержание": "maintain"
    }

    db.update_user(message.from_user.id, goal=goals[message.text])
    await message.answer("✅ цель установлена")

# ================= FULL GYM EXERCISES =================
@router.message(F.text == "🏋️ Тренировки ЗАЛ")
async def gym(message: Message):

    await message.answer(
        "🏋️ ПОЛНЫЙ ЗАЛ (СПИСОК УПРАЖНЕНИЙ)\n\n"

        "💪 ГРУДЬ:\n"
        "- жим лёжа\n- жим гантелей\n- кроссовер\n- отжимания на брусьях\n\n"

        "🏋️ СПИНА:\n"
        "- тяга штанги\n- подтягивания\n- тяга верхнего блока\n- тяга гантели\n\n"

        "🦵 НОГИ:\n"
        "- присед\n- жим ногами\n- разгибание ног\n- сгибание ног\n\n"

        "💪 ПЛЕЧИ:\n"
        "- жим вверх\n- махи гантелями\n- махи в стороны\n\n"

        "💪 РУКИ:\n"
        "- бицепс\n- трицепс\n- молот\n\n"

        "🔥 ПРЕСС:\n"
        "- скручивания\n- подъём ног\n- планка\n\n"

        "🏃 КАРДИО:\n"
        "- бег\n- скакалка\n- эллипс"
    )

# ================= FOOD =================
@router.message(F.text == "🍽 Питание")
async def food(message: Message):

    user = db.get_user(message.from_user.id)
    goal = user.get("goal", "maintain")

    data = {
        "gain": "💪 НАБОР: рис, курица, яйца, орехи (+300-500 ккал)",
        "loss": "🔥 ПОХУДЕНИЕ: курица, рыба, овощи (-400 ккал)",
        "maintain": "⚖️ БАЛАНС: белки + жиры + углеводы"
    }

    await message.answer(data[goal])

# ================= CALORIES COUNTER =================
@router.message(F.text == "🔥 Счётчик калорий")
async def calories(message: Message):
    await message.answer(
        "🔥 КАЛОРИИ\n\n"
        "Напиши:\n"
        "вес рост возраст\n\n"
        "Пример:\n"
        "70 180 20"
    )

@router.message(F.text.regexp(r"^\d+\s\d+\s\d+$"))
async def calc(message: Message):

    w, h, a = map(int, message.text.split())

    bmr = 10*w + 6.25*h - 5*a + 5
    calories = int(bmr * 1.5)

    await message.answer(
        f"📊 РЕЗУЛЬТАТ:\n"
        f"BMR: {int(bmr)}\n"
        f"КАЛОРИИ: {calories}\n\n"
        f"💪 масса: +300\n🔥 похудение: -400"
    )

# ================= AI TRAINER =================
@router.message(F.text.startswith("🤖"))
async def ai(message: Message):

    user = db.get_user(message.from_user.id)

    text = message.text.replace("🤖", "").strip()

    if not text:
        return await message.answer("Напиши вопрос после 🤖")

    answer = fitness_ai(user.get("goal", "maintain"), text)

    await message.answer(answer)

# ================= REGISTER =================
def register_all_handlers(dp):
    dp.include_router(router)