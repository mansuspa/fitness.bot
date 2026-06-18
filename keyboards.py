from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Main Menu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 МЕНЮ")],
        [KeyboardButton(text="🔥 ПОХУДЕНИЕ"), KeyboardButton(text="⚖️ МАССА")],
        [KeyboardButton(text="🏋️ ТРЕНИРОВКИ"), KeyboardButton(text="🥗 ПИТАНИЕ")],
        [KeyboardButton(text="📊 СТАТИСТИКА"), KeyboardButton(text="💎 PREMIUM")]
    ],
    resize_keyboard=True
)

# Goal Selection
goal_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 ПОХУДЕНИЕ")],
        [KeyboardButton(text="⚖️ НАБОР МАССЫ")],
        [KeyboardButton(text="↩️ НАЗАД")]
    ],
    resize_keyboard=True
)

# Training Menu
training_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Программа на неделю")],
        [KeyboardButton(text="🏋️ Упражнение дня")],
        [KeyboardButton(text="✅ Отметить тренировку")],
        [KeyboardButton(text="↩️ НАЗАД")]
    ],
    resize_keyboard=True
)

# Nutrition Menu
nutrition_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽️ План питания")],
        [KeyboardButton(text="⚖️ Расчет калорий")],
        [KeyboardButton(text="🥗 Рецепты")],
        [KeyboardButton(text="↩️ НАЗАД")]
    ],
    resize_keyboard=True
)

# Premium Menu (Inline)
premium_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💎 Активировать Premium", callback_data="buy_premium")],
        [InlineKeyboardButton(text="ℹ️ Что входит?", callback_data="premium_info")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close")]
    ]
)

# Stats Input
stats_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚖️ Вес")],
        [KeyboardButton(text="📏 Рост")],
        [KeyboardButton(text="🎂 Возраст")],
        [KeyboardButton(text="✅ Готово")],
        [KeyboardButton(text="↩️ НАЗАД")]
    ],
    resize_keyboard=True
)