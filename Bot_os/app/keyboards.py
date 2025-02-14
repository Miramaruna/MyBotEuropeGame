from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

button_start = [
    [KeyboardButton(text="/register"), KeyboardButton(text="/info")],
    [KeyboardButton(text="/country_info"), KeyboardButton(text="/countries")],
    [KeyboardButton(text="/start"), KeyboardButton(text="/info_bot")], 
    [KeyboardButton(text="/help"), KeyboardButton(text="/admin")],
    [KeyboardButton(text="/map"), KeyboardButton(text="Копать")],
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
    [KeyboardButton(text="/ban"), KeyboardButton(text="/get_users")],
    [KeyboardButton(text="/mailing"), KeyboardButton(text="/givement")],
    [KeyboardButton(text="/admin"), KeyboardButton(text="/register_admin")],
    [KeyboardButton(text="/get_country"), KeyboardButton(text="/create_country")],
    [KeyboardButton(text="/delete_country"), KeyboardButton(text="/info_bot")],
    [KeyboardButton(text="/help"), KeyboardButton(text="/start")],
    [KeyboardButton(text="/ban_admin")]
]

keyboard_admin = ReplyKeyboardMarkup(keyboard=button_admin, resize_keyboard=True, row_width=2)

army = [
    [InlineKeyboardButton(text='Увеличить кол. Людей', callback_data='add')],
    [InlineKeyboardButton(text='start', callback_data='st'), InlineKeyboardButton(text='stop', callback_data='sp')]
]

arm_kb = InlineKeyboardMarkup(inline_keyboard=army)

ar = [
    [InlineKeyboardButton(text='Ad. Soldiers', callback_data='sol')],
    [InlineKeyboardButton(text='Ad. Cars', callback_data='car')],
    [InlineKeyboardButton(text='Ad. Tanks', callback_data='tan')]
]
armmy_kb = InlineKeyboardMarkup(inline_keyboard=ar)

button_army_peace = [
    [KeyboardButton(text='обьявить войну'), KeyboardButton(text='обьявить перемирие')]
]

keyboard_army_peace = ReplyKeyboardMarkup(keyboard=button_army_peace, resize_keyboard=True, row_width=2)