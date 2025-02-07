from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

button_start = [
    [KeyboardButton(text="/register")],
    [KeyboardButton(text="/info")],
    [KeyboardButton(text="/country_info")],
    [KeyboardButton(text="/countries")],
    [KeyboardButton(text="/start")],
    [KeyboardButton(text="/help")],
    [KeyboardButton(text="/info_bot")]
    [KeyboardButton(text="Копать")]
]

keyboard_start = ReplyKeyboardMarkup(keyboard=button_start, resize_keyboard=True, row_width=2)

button_countries_methods = [
    [InlineKeyboardButton(text="Начать производство", callback_data="start_production")],
    [InlineKeyboardButton(text="Закончить производство", callback_data="stop_production")],
    [InlineKeyboardButton(text="Инвестировать", callback_data="invest")],
]

keyboard_countries_methods = InlineKeyboardMarkup(inline_keyboard=button_countries_methods)

button_admin = [
    [KeyboardButton(text="/ban")],
    [KeyboardButton(text="/get_users")],
    [KeyboardButton(text="/mailing")],
    [KeyboardButton(text="/givement")],
    [KeyboardButton(text="/admin")],
    [KeyboardButton(text="/register_admin")]
]

keyboard_admin = ReplyKeyboardMarkup(keyboard=button_admin, resize_keyboard=True, row_width=2)