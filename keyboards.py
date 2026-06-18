import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

def get_main_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽️ Питание", callback_data="menu_food"),
            InlineKeyboardButton(text="💪 Тренировки", callback_data="menu_workout"),
        ],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings"),
        ],
    ])
    return keyboard

def get_food_keyboard():
    """Клавиатура для модуля питания"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Рассчитать калории", callback_data="food_calories"),
            InlineKeyboardButton(text="📝 Мой рацион", callback_data="food_meals"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back"),
        ],
    ])
    return keyboard

def get_workout_keyboard():
    """Клавиатура для модуля тренировок"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏋️ Верх тела", callback_data="workout_upper"),
            InlineKeyboardButton(text="🏋️ Низ тела", callback_data="workout_lower"),
        ],
        [
            InlineKeyboardButton(text="💪 Кардио", callback_data="workout_cardio"),
            InlineKeyboardButton(text="🧘 Растяжка", callback_data="workout_stretch"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back"),
        ],
    ])
    return keyboard

def get_profile_keyboard():
    """Клавиатура для профиля"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="profile_edit"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back"),
        ],
    ])
    return keyboard

def get_settings_keyboard():
    """Клавиатура для настроек"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications"),
            InlineKeyboardButton(text="🌙 Тёмная тема", callback_data="settings_theme"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back"),
        ],
    ])
    return keyboard