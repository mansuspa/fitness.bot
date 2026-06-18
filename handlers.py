import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from database import Database
from nutrition import Nutrition
from workout import Workout

logger = logging.getLogger(__name__)

router = Router()

db = Database()
nutrition = Nutrition()
workout = Workout()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"

    try:
        db.add_user(user_id, username)
    except Exception:
        pass

    await message.answer(
        f"💪 Привет, {username}!\n\n"
        f"Я персональный фитнес-тренер.\n\n"
        f"Команды:\n"
        f"/menu\n"
        f"/workout\n"
        f"/food\n"
        f"/profile\n"
        f"/help"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 Справка\n\n"
        "/start - запуск\n"
        "/menu - меню\n"
        "/food - питание\n"
        "/workout - тренировки\n"
        "/profile - профиль"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🏠 Главное меню\n\n"
        "💪 /workout\n"
        "🥗 /food\n"
        "👤 /profile\n"
        "⚙️ /settings"
    )


@router.message(Command("food"))
async def cmd_food(message: Message):
    await message.answer(
        "🥗 ПИТАНИЕ\n\n"
        "Для похудения:\n"
        "🍗 Курица 200 г\n"
        "🐟 Рыба 200 г\n"
        "🥗 Овощи 300-500 г\n"
        "💧 Вода 2-3 литра\n\n"
        "Для массы:\n"
        "🍗 Курица 250 г\n"
        "🍚 Рис 200 г\n"
        "🥚 Яйца 5 шт\n"
        "🥛 Творог 200 г"
    )


@router.message(Command("workout"))
async def cmd_workout(message: Message):
    await message.answer(
        "💪 ТРЕНИРОВКА\n\n"
        "🏋️ Грудь:\n"
        "Жим лёжа 4×10\n"
        "Жим гантелей 3×12\n"
        "Разводка 3×15\n\n"
        "🏋️ Спина:\n"
        "Подтягивания 4×10\n"
        "Тяга блока 4×12\n\n"
        "🏋️ Ноги:\n"
        "Приседания 4×10\n"
        "Жим ногами 4×12"
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id

    try:
        user_data = db.get_user(user_id)

        if user_data:
            await message.answer(
                f"👤 Профиль\n\n"
                f"ID: {user_id}\n"
                f"Имя: {user_data.get('username', '-')}"
            )
            return

    except Exception:
        pass

    await message.answer("Профиль пока пустой.")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    await message.answer("⚙️ Настройки скоро появятся.")


@router.message()
async def ai_fitness(message: Message):
    text = (message.text or "").lower()

    if "пресс" in text:
        await message.answer(
            "🔥 ПРЕСС\n\n"
            "Скручивания 4×20\n"
            "Планка 3×60 сек\n"
            "Подъём ног 4×15"
        )
        return

    if "груд" in text:
        await message.answer(
            "💪 ГРУДЬ\n\n"
            "Жим лёжа 4×10\n"
            "Жим гантелей 3×12\n"
            "Разводка 3×15"
        )
        return

    if "спина" in text:
        await message.answer(
            "🏋️ СПИНА\n\n"
            "Подтягивания 4×10\n"
            "Тяга верхнего блока 4×12\n"
            "Тяга штанги 4×10"
        )
        return

    if "ног" in text:
        await message.answer(
            "🦵 НОГИ\n\n"
            "Приседания 4×10\n"
            "Жим ногами 4×12\n"
            "Выпады 3×12"
        )
        return

    if "похуд" in text:
        await message.answer(
            "🔥 ПОХУДЕНИЕ\n\n"
            "Кардио 30 минут\n"
            "Дефицит калорий\n"
            "3-4 тренировки в неделю"
        )
        return

    if "масса" in text:
        await message.answer(
            "💪 НАБОР МАССЫ\n\n"
            "Профицит калорий\n"
            "Базовые упражнения\n"
            "Сон 7-9 часов"
        )
        return

    await message.answer(
        "🤖 Я фитнес-тренер.\n\n"
        "Напиши:\n"
        "• пресс\n"
        "• грудь\n"
        "• спина\n"
        "• ноги\n"
        "• похудение\n"
        "• масса"
    )


def register_all_handlers(dp):
    dp.include_router(router)
    logger.info("Все обработчики зарегистрированы")