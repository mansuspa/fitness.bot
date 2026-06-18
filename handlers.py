import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from database import Database
from trainer import FitnessTrainer
from keyboards import (
    main_menu, goal_menu, training_menu, nutrition_menu, 
    premium_menu, stats_menu
)
from config import TRAINING_PLANS, PREMIUM_BENEFITS

logger = logging.getLogger(__name__)
router = Router()

# Global state for stats input
user_stats_state = {}


# ============ START & MENU ============

@router.message(CommandStart())
async def start(message: Message):
    """Start command handler"""
    try:
        uid = str(message.from_user.id)
        users = Database.load()
        user = Database.get_or_create_user(uid, message.from_user.first_name, users)
        
        await message.answer(
            "💪 FITNESS AI TRAINER PRO\n\n"
            f"Привет, {user['name']}! 🔥\n\n"
            "Я твой персональный фитнес-тренер. Помогу тебе:\n"
            "✅ Построить программу тренировок\n"
            "✅ Составить план питания\n"
            "✅ Отслеживать прогресс\n"
            "✅ Дать профессиональный совет\n\n"
            "Начнём? Выбери опцию ниже 👇",
            reply_markup=main_menu
        )
    except Exception as e:
        logger.error(f"START ERROR: {e}")
        await message.answer("⚠️ Ошибка, попробуй /start")


@router.message(F.text == "🏠 МЕНЮ")
async def menu(message: Message):
    """Main menu"""
    await message.answer("📋 Главное меню", reply_markup=main_menu)


# ============ GOALS ============

@router.message(F.text == "🔥 ПОХУДЕНИЕ")
async def set_fat_loss(message: Message):
    """Set fat loss goal"""
    uid = str(message.from_user.id)
    users = Database.load()
    
    Database.update_user(uid, {"goal": "fat_loss"}, users)
    users = Database.load()
    
    await message.answer(
        "🎯 ЦЕЛЬ: ПОХУДЕНИЕ\n\n"
        "Отлично! Вот что нас ждет:\n"
        "🔥 Кардио + Силовые\n"
        "🥗 Дефицит калорий 500-700\n"
        "💧 Много воды\n"
        "😴 Качественный сон\n\n"
        "Теперь заполни свои параметры",
        reply_markup=stats_menu
    )


@router.message(F.text == "⚖️ МАССА")
async def set_mass(message: Message):
    """Set mass gain goal"""
    uid = str(message.from_user.id)
    users = Database.load()
    
    Database.update_user(uid, {"goal": "mass"}, users)
    
    await message.answer(
        "🎯 ЦЕЛЬ: НАБОР МАССЫ\n\n"
        "Отлично! Вот что нас ждет:\n"
        "💪 Тяжелая силовая\n"
        "🍗 Профицит калорий 300-500\n"
        "💧 Много воды\n"
        "😴 Качественный сон\n\n"
        "Теперь заполни свои параметры",
        reply_markup=stats_menu
    )


# ============ TRAINING ============

@router.message(F.text == "🏋️ ТРЕНИРОВКИ")
async def training_menu_handler(message: Message):
    """Training menu"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Сначала выбери цель тренировок", reply_markup=main_menu)
        return
    
    await message.answer("🏋️ Выбери что хочешь", reply_markup=training_menu)


@router.message(F.text == "📅 Программа на неделю")
async def weekly_plan(message: Message):
    """Show weekly training plan"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Выбери цель первым делом")
        return
    
    plan = FitnessTrainer.get_weekly_plan(user["goal"])
    await message.answer(plan, reply_markup=training_menu)


@router.message(F.text == "🏋️ Упражнение дня")
async def daily_workout(message: Message):
    """Show daily workout"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Выбери цель первым делом")
        return
    
    workout = FitnessTrainer.get_daily_workout(user["goal"])
    await message.answer(workout, reply_markup=training_menu)


@router.message(F.text == "✅ Отметить тренировку")
async def log_workout(message: Message):
    """Log workout completion"""
    uid = str(message.from_user.id)
    users = Database.load()
    
    Database.add_workout(uid, {"exercise": "Тренировка завершена"}, users)
    
    await message.answer(
        "✅ Отлично! Тренировка отмечена!\n\n"
        "💪 Ты становишься сильнее с каждой тренировкой!",
        reply_markup=training_menu
    )


# ============ NUTRITION ============

@router.message(F.text == "🥗 ПИТАНИЕ")
async def nutrition_menu_handler(message: Message):
    """Nutrition menu"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Сначала выбери цель тренировок", reply_markup=main_menu)
        return
    
    await message.answer("🥗 Выбери что интересует", reply_markup=nutrition_menu)


@router.message(F.text == "🍽️ План питания")
async def nutrition_plan(message: Message):
    """Show nutrition plan"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Выбери цель первым делом")
        return
    
    plan = FitnessTrainer.get_nutrition_plan(user["goal"])
    await message.answer(plan, reply_markup=nutrition_menu)


@router.message(F.text == "⚖️ Расчет калорий")
async def calorie_calculator(message: Message):
    """Calculate daily calories"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Выбери цель первым делом")
        return
    
    stats = user.get("stats", {})
    weight = stats.get("weight")
    height = stats.get("height")
    age = stats.get("age")
    gender = stats.get("gender")
    
    if not all([weight, height, age, gender]):
        await message.answer("❗ Заполни сначала свои параметры в профиле", reply_markup=nutrition_menu)
        return
    
    calories = FitnessTrainer.calculate_calories(weight, height, age, gender, user["goal"])
    
    text = f"⚖️ РАСЧЕТ КАЛОРИЙ\n\n"
    text += f"📊 Базовый метаболизм: {calories['bmr']} ккал\n"
    text += f"📈 Суточный расход: {calories['tdee']} ккал\n"
    text += f"🎯 Твоя норма: {calories['daily_target']} ккал\n\n"
    text += f"💪 Белок: {calories['protein']}g\n"
    text += f"🍚 Углеводы: {calories['carbs']}g\n"
    text += f"💧 Жиры: 50-70g\n\n"
    text += f"💡 Помни: Ешь медленнее, пей больше воды!"
    
    await message.answer(text, reply_markup=nutrition_menu)


# ============ STATISTICS ============

@router.message(F.text == "📊 СТАТИСТИКА")
async def statistics(message: Message):
    """Show user statistics"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user:
        await message.answer("❗ Профиль не найден")
        return
    
    stats = Database.get_user_stats(uid, users)
    goal_name = TRAINING_PLANS.get(stats["goal"], {}).get("name", "Не выбрана")
    
    text = f"📊 ТОВ ПРОФИЛЬ\n\n"
    text += f"👤 Имя: {user['name']}\n"
    text += f"🎯 Цель: {goal_name}\n"
    text += f"💎 Premium: {'✅' if stats['premium'] else '❌'}\n"
    text += f"🏋️ Тренировок: {stats['total_workouts']}\n\n"
    
    if stats["stats"]["weight"]:
        text += f"⚖️ Вес: {stats['stats']['weight']} kg\n"
    if stats["stats"]["height"]:
        text += f"📏 Рост: {stats['stats']['height']} cm\n"
    if stats["stats"]["age"]:
        text += f"🎂 Возраст: {stats['stats']['age']} лет\n"
    if stats["daily_calories"]:
        text += f"🥗 Калории: {stats['daily_calories']} ккал\n"
    
    await message.answer(text, reply_markup=main_menu)


# ============ PREMIUM ============

@router.message(F.text == "💎 PREMIUM")
async def premium_menu_handler(message: Message):
    """Show premium menu"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if user and user.get("premium"):
        await message.answer("💎 Premium уже активирован!\n\nТеперь тебе доступны все фишки!", reply_markup=main_menu)
        return
    
    text = "💎 PREMIUM - Премиум тренер\n\n"
    for benefit in PREMIUM_BENEFITS:
        text += f"{benefit}\n"
    text += f"\n💰 Цена: 99 рублей в месяц"
    
    await message.answer(text, reply_markup=premium_menu)


@router.callback_query(F.data == "buy_premium")
async def buy_premium(query: CallbackQuery):
    """Buy premium subscription"""
    uid = str(query.from_user.id)
    users = Database.load()
    
    Database.update_user(uid, {"premium": True}, users)
    
    await query.answer("✅ Premium активирован!", show_alert=True)
    await query.message.edit_text("💎 PREMIUM АКТИВИРОВАН! 🚀\n\nСпасибо! Начни использовать все возможности!")


@router.callback_query(F.data == "premium_info")
async def premium_info(query: CallbackQuery):
    """Show premium info"""
    text = "💎 ЧТО ВХОДИТ В PREMIUM:\n\n"
    for benefit in PREMIUM_BENEFITS:
        text += f"{benefit}\n"
    
    await query.answer()
    await query.message.edit_text(text, reply_markup=premium_menu)


@router.callback_query(F.data == "close")
async def close_menu(query: CallbackQuery):
    """Close inline menu"""
    await query.message.delete()
    await query.answer()


# ============ AI TRAINER - FREE TEXT ============

@router.message()
async def ai_trainer(message: Message):
    """AI trainer - respond to free text"""
    uid = str(message.from_user.id)
    users = Database.load()
    user = users.get(uid)
    
    if not user or not user.get("goal"):
        await message.answer("❗ Сначала выбери цель в меню", reply_markup=main_menu)
        return
    
    advice = FitnessTrainer.get_ai_advice(message.text, user["goal"])
    await message.answer(advice, reply_markup=main_menu)