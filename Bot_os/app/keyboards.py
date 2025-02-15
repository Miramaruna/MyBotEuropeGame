from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

button_start = [
    [KeyboardButton(text="/start")],
    [KeyboardButton(text="/register"), KeyboardButton(text="/unlogin")],
    [KeyboardButton(text="/country_info"), KeyboardButton(text="/countries")],
    [KeyboardButton(text="/info"), KeyboardButton(text="/info_bot"), KeyboardButton(text="/help")], 
    [KeyboardButton(text="/admin")],
    [KeyboardButton(text="/list_population"), KeyboardButton(text='/list_economy')],
    [KeyboardButton(text="Копать"), KeyboardButton(text="дать"), KeyboardButton(text="/map")],
    [KeyboardButton(text="Армия")]
]

keyboard_start = ReplyKeyboardMarkup(keyboard=button_start, resize_keyboard=True, row_width=2)

button_countries_methods = [
    [InlineKeyboardButton(text="Начать производство", callback_data="start_production")],
    [InlineKeyboardButton(text="Закончить производство", callback_data="stop_production")],
    [InlineKeyboardButton(text="Начать раздачу таваров", callback_data="start_population")],
    [InlineKeyboardButton(text="Закончить раздачу товаров", callback_data="stop_population")],
    [InlineKeyboardButton(text="Провести праздник", callback_data="start_party_happy")],
    [InlineKeyboardButton(text="Инвестировать", callback_data="invest")]
]

keyboard_countries_methods = InlineKeyboardMarkup(inline_keyboard=button_countries_methods)

button_admin = [
    [KeyboardButton(text="/admin"), KeyboardButton(text="/ban"), KeyboardButton(text="/mailing")],
    [KeyboardButton(text="update_country")],
    [KeyboardButton(text="/register_admin"), KeyboardButton(text="/ban_admin")],
    [KeyboardButton(text="/get_country"), KeyboardButton(text="/get_users")],
    [KeyboardButton(text="/delete_country"), KeyboardButton(text="/create_country")],
    [KeyboardButton(text="/help"), KeyboardButton(text="/start"), KeyboardButton(text="/info_bot")],
    [KeyboardButton(text="/givement")]
]

keyboard_admin = ReplyKeyboardMarkup(keyboard=button_admin, resize_keyboard=True, row_width=2)

ar = [
    [InlineKeyboardButton(text='Ad. Soldiers', callback_data='sol'), InlineKeyboardButton(text='Ad. Cars', callback_data='car')],
    [InlineKeyboardButton(text='Ad. Tanks', callback_data='tan')]
]
armmy_kb = InlineKeyboardMarkup(inline_keyboard=ar)

button_army_peace = [
    [KeyboardButton(text='обьявить войну'), KeyboardButton(text='обьявить перемирие')],
    [KeyboardButton(text='сражаться')]
]

keyboard_army_peace = ReplyKeyboardMarkup(keyboard=button_army_peace, resize_keyboard=True, row_width=2)