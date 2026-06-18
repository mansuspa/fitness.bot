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

        [KeyboardButton(text="🏋️ Тренировки")],
        [KeyboardButton(text="🍽 Питание")],
        [KeyboardButton(text="🧠 SMART режим")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------
@router.message(CommandStart())
async def start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "💪 FITNESS SMART V7\nВыбери цель:",
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

    # FIX: update_user (у тебя в DB так называется)
    db.update_user(message.from_user.id, goal=goals[message.text])

    await message.answer("цель установлена ✅")

# ---------------- SMART TRAINING MENU ----------------
@router.message(F.text == "🏋️ Тренировки")
async def training_menu(message: Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💪 Грудь"), KeyboardButton(text="🏋️ Спина")],
            [KeyboardButton(text="🦵 Ноги"), KeyboardButton(text="💪 Плечи")],
            [KeyboardButton(text="💪 Руки"), KeyboardButton(text="🔥 Пресс")],
            [KeyboardButton(text="🏃 Кардио")]
        ],
        resize_keyboard=True
    )

    await message.answer("выбери группу мышц 👇", reply_markup=kb)

# ---------------- EXERCISES (100% ORIGINAL) ----------------
@router.message(F.text == "💪 Грудь")
async def chest(message: Message):
    await message.answer(
        "💪 ГРУДЬ\n\n"
        "1. Жим лёжа — 4x8-12\n"
        "👉 техника: лопатки сведены, штанга к груди\n\n"
        "2. Жим гантелей — 3x10\n"
        "👉 опускай медленно\n\n"
        "❌ ошибки:\n"
        "- не отрывай ягодицы\n"
        "- не разводи локти сильно"
    )

@router.message(F.text == "🏋️ Спина")
async def back(message: Message):
    await message.answer(
        "🏋️ СПИНА\n\n"
        "1. Тяга штанги — 4x10\n"
        "👉 спина ровная\n\n"
        "2. Подтягивания — 3x макс\n"
        "👉 без раскачки\n\n"
        "❌ ошибки:\n"
        "- округление спины"
    )

@router.message(F.text == "🦵 Ноги")
async def legs(message: Message):
    await message.answer(
        "🦵 НОГИ\n\n"
        "1. Присед — 4x10\n"
        "👉 колени в сторону носков\n\n"
        "2. Жим ногами — 3x12\n"
        "👉 полный контроль\n\n"
        "❌ ошибки:\n"
        "- не заваливай колени внутрь"
    )

@router.message(F.text == "💪 Плечи")
async def shoulders(message: Message):
    await message.answer(
        "💪 ПЛЕЧИ\n\n"
        "1. Жим вверх — 4x10\n"
        "👉 не прогибай поясницу\n\n"
        "2. Разводка — 3x12\n"
        "👉 медленно"
    )

@router.message(F.text == "💪 Руки")
async def arms(message: Message):
    await message.answer(
        "💪 РУКИ\n\n"
        "1. Бицепс — 3x12\n"
        "👉 без рывков\n\n"
        "2. Трицепс — 3x12\n"
        "👉 локти фиксированы"
    )

@router.message(F.text == "🔥 Пресс")
async def abs(message: Message):
    await message.answer(
        "🔥 ПРЕСС\n\n"
        "1. Скручивания — 3x20\n"
        "2. Планка — 1-2 мин\n"
        "3. Подъём ног — 3x15"
    )

@router.message(F.text == "🏃 Кардио")
async def cardio(message: Message):
    await message.answer(
        "🏃 КАРДИО\n\n"
        "1. Бег — 20-40 мин\n"
        "2. Скакалка — 10 мин\n"
        "3. HIIT — 15-20 мин"
    )

# ---------------- FOOD SMART (НЕ ТРОГАЛ) ----------------
@router.message(F.text == "🍽 Питание")
async def food(message: Message):

    user = db.get_user(message.from_user.id)

    if not user:
        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    if goal == "gain":
        text = "💪 НАБОР МАССЫ\n\n🍽 ешь:\n- рис\n- курица\n- яйца\n- овсянка\n\n💡 +300-500 ккал"
    elif goal == "loss":
        text = "🔥 ПОХУДЕНИЕ\n\n🍽 ешь:\n- курица\n- рыба\n- овощи\n\n❌ убери сахар\n💡 -400 ккал"
    else:
        text = "⚖️ ПОДДЕРЖАНИЕ\n\n🍽 баланс:\n- мясо\n- крупы\n- овощи"

    await message.answer(text)

# ---------------- SMART MODE (FIX SAFE) ----------------
@router.message(F.text == "🧠 SMART режим")
async def smart(message: Message):

    user = db.get_user(message.from_user.id)

    if not user:
        return await message.answer("нажми /start")

    goal = user.get("goal", "maintain")

    if goal == "gain":
        rec = "💪 тебе нужно 4-5 тренировок/нед"
    elif goal == "loss":
        rec = "🔥 добавь кардио + дефицит калорий"
    else:
        rec = "⚖️ держи баланс + 3 тренировки"

    await message.answer(
        "🧠 SMART анализ\n\n"
        f"🎯 цель: {goal}\n"
        f"📌 рекомендация:\n{rec}"
    )

# ---------------- FALLBACK ----------------
@router.message()
async def fallback(message: Message):
    await message.answer("выбери кнопку 👇", reply_markup=menu)


def register_all_handlers(dp):
    dp.include_router(router)