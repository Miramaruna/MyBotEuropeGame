from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

button_start = [
    KeyboardButton(text="/register"), KeyboardButton(text="/info"),
    KeyboardButton(text="/country_info"), KeyboardButton(text="/invest"),
    KeyboardButton(text="/countries"), KeyboardButton(text="/start"),
    KeyboardButton(text="/help")
]