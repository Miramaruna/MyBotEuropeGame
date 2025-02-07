
import sqlite3, random, time, asyncio

from aiogram import F, Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery, BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import ChatMemberUpdatedFilter

from aiogram import types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ContentType, ChatMemberUpdated
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus

from app.keyboards import *
from app.DB import *
from bot import *

r = Router()
fm_t = False
chat_id = None
admin = 5626265763 

class Investigate(StatesGroup):
    num = State()

@r.message(Command("invest"))
async def investigate(message: Message, state: FSMContext):
    await message.reply("Введите сумму инвестиции на вашу страну:")
    await state.set_state(Investigate.num)
    
@r.message(Investigate.num)
async def process_investigate(message: Message, state: FSMContext):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT money FROM users WHERE user_id = ?", (message.from_user.id,))
    cursor.execute("SELECT country FROM user WHERE user_id = ?", (message.from_user.id,))
    country = cursor.fetchone()[0]
    money = cursor.fetchone()[0]
    if country is None:
        await message.reply("У вас нет страны.")
        await state.clear()
        return
    if money < int(message.text):
        await message.reply("У вас недостаточно денег.")
        await state.clear()
        return
    asyncio.create_task(country, money)
    await state.clear()
    conn.close()
    await message.reply("Вы успешно инвестировали деньги в экономику своей страны.")

async def create_task(country, money):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    Invest = True
    numOfInvest = 0
    while Invest:
        numOfInvest += 1
        if numOfInvest == 5:
            Invest = False
            break
        await asyncio.sleep(5)
        cursor.execute("UPDATE countries SET economy = economy + ? WHERE name = ?", (money / 3, country))
        await message.reply(F"Вы инвестировали {money / 3} монет в экономику своей страны.")
    await state.clear()
    conn.commit()