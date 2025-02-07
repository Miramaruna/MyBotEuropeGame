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
kol_kop = None

# region InCountryMethods

class Investigate(StatesGroup):
    num = State()

@r.message(Command("invest"))
async def investigate(message: Message, state: FSMContext):
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.reply("Вы не зарегистрированы.")
        return
    await message.reply("Введите сумму инвестиции на вашу страну:")
    await state.set_state(Investigate.num)
    
@r.message(Investigate.num)
async def process_investigate(message: Message, state: FSMContext):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT money FROM users WHERE user_id = ?", (message.from_user.id,))
        cursor.execute("SELECT country FROM users WHERE user_id = ?", (message.from_user.id,))
        country = cursor.fetchone()[0]
        money = cursor.fetchone()[0]
    except BaseException as e:
        await message.reply("Error: " + str(e))
        await state.clear()
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
        try:
            cursor.execute("UPDATE countries SET economy = economy + ? WHERE name = ?", (money / 3, country))
            await message.reply(F"Вы инвестировали {money / 3} монет в экономику своей страны.")
        except BaseException as e:
            await message.reply("Error: " + str(e))
            Invest = False
            break
    await state.clear()
    conn.commit()
    
# endregion
    
@r.message(F.text.in_({"копать", "Копать", "rjgfnm", "Rjgfnm"}))
async def kop(message: Message):
    global kol_kop
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.reply("Вы не зарегистрированы.")
        return
    if kol_kop is None:
        kol_kop = 0
    if kol_kop < 10:
        kol_kop += 1
    elif kol_kop >= 10:
        await message.reply("Вы уже копали 10 раз.")
        return
    cursor.execute("UPDATE users SET money = money + 100 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await message.reply("Вы успешно заработали 100 монет.")
    
@r.message(Command("help"))
async def help(message: Message):
    await message.reply("Список доступных комманд:\n/start - начать игру\n/register - зарегистрироваться\n/invest - инвестировать деньги в экономику\n/countries - список стран\nКопать - заработать денег\n/info - информация о вас\n/country_info - информация о вашей стране\n/help - помощь")
    
#region Need methods
    
async def chek_is_user(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False
    conn.close()
    
# endregion