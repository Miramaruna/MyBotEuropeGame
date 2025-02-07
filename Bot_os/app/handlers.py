# region imports

import sqlite3, random, time, asyncio, logging


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
from config import *

# endregion

r = Router()
fm_t = False
chat_id = None
admin = 5626265763 
kol_kop = None

# region InCountryMethods

class Investigate(StatesGroup):
    num = State()

@r.callback_query(F.data == "invest")
async def investigate(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("💰 Введите сумму инвестиции на вашу страну:\n🚫Отмена - отмена")
    await state.set_state(Investigate.num)
    
@r.message(Investigate.num)
async def process_investigate(message: Message, state: FSMContext):
    global numOfInvest, Invest
    if message.text == "Отмена":
        Invest = False
        await state.clear()
        return
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    is_user = await chek_is_user(message.from_user.id)
    money = await get_money(message.from_user.id)
    country = await get_country(message.from_user.id)
    if is_user == False:
        await message.reply("❌ Вы не зарегистрированы.")
        return
    try:
        if money < int(message.text):
            await message.reply("⚠ У вас недостаточно средств для инвестирования.")
            return
        try:
            await transfer_money(message.from_user.id, int(message.text), False)
            asyncio.create_task(invest_task(country, int(message.text), message.from_user.id))
        except BaseException as e:
            await message.reply("🚨 Ошибка: " + str(e))
            Invest = False
            return
    except BaseException as e:
        await message.reply("� Ошибка: " + str(e))
        Invest = False
        return
        await state.clear()
        conn.commit()
        conn.close()

async def invest_task(country, money, chat_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    Invest = True
    numOfInvest = 0
    while Invest:
        numOfInvest += 1
        if numOfInvest == 6:
            Invest = False
            break
        try:
            cursor.execute("UPDATE countries SET economy = economy + ? WHERE name = ?", (money // 3, country))
            await bot.send_message(chat_id=chat_id, text=f"✅ Было получено {money // 3} единиц экономики вашей страны.")
        except BaseException as e:
            await bot.send_message(chat_id=chat_id, text="🚨 Ошибка: " + str(e))
            Invest = False
            break
        await asyncio.sleep(20)
    conn.commit()
    conn.close()

# endregion
    
# region earn money

@r.message(F.text.in_({"копать", "Копать", "rjgfnm", "Rjgfnm"}))
async def kop(message: Message):
    global kol_kop
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.reply("❌ Вы не зарегистрированы.")
        return
    if kol_kop is None:
        kol_kop = 0
    if kol_kop < 10:
        kol_kop += 1
    elif kol_kop >= 10:
        await message.reply("⛏ Вы уже копали 10 раз.")
        return
    cursor.execute("UPDATE users SET money = money + 100 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await message.reply("💰 Вы успешно заработали 100 монет.", reply_markup=keyboard_start)
    
@r.callback_query(F.data == "start_production")
async def money_from_country(callback_query: types.CallbackQuery):
    global fm_t
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    is_user = await chek_is_user(user_id)
    if is_user == False:
        await callback_query.answer("❌ Вы не зарегистрированы.")
        fm_t = False
        return
    await callback_query.answer("🏭 Производство начато.\n⏳Каждую минуту вы будете получать свой доход.")
    fm_t = True
    while fm_t:
        country = await get_country(user_id)
        params = await get_country_params(country)
        economy = params[0] // 5
        population = params[1] // 4
        happiness = params[2] // 12
        income = economy + population * happiness
        await transfer_money(income, user_id, True)
        await bot.send_message(chat_id=chat_id, text=f"💰 Было получено {income} монет из страны {country}.")
        await asyncio.sleep(5)
        
@r.callback_query(F.data == "stop_production")
async def stop_production(callback_query: types.CallbackQuery):
    global fm_t
    await callback_query.answer("🛑 Производство остановлено.")
    fm_t = False
# endregion
    
@r.message(Command("help"))
async def help(message: Message):
    await message.reply("📜 Список доступных команд:\n"
                        "/start - 🏁 Начать игру\n"
                        "/register - 📝 Зарегистрироваться\n"
                        "/invest - 💰 Инвестировать деньги в экономику\n"
                        "/countries - 🌎 Список стран\n"
                        "Копать - ⛏ Заработать денег\n"
                        "/info - ℹ Информация о вас\n"
                        "/country_info - 🌍 Информация о вашей стране\n"
                        "/help - ❓ Помощь", reply_markup=keyboard_start)
    
@r.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фота: {message.photo[-1].file_id}")
    
# region Need methods

async def add_admin(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="❗️Ошибка: " + str(e))
        return False
    conn.commit()
    conn.close()
    return True

async def transfer_money(money, user_id, is_positive):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    try:
        if is_positive:
            cursor.execute("UPDATE users SET money = money + ? WHERE user_id =?", (money, user_id))
        else:
            cursor.execute("UPDATE users SET money = money - ? WHERE user_id =?", (money, user_id))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨 Ошибка: " + str(e))
        return False
    conn.commit()
    conn.close()
    return True
    
async def chek_is_user(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False
    conn.close()
    
async def get_money(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT money FROM users WHERE user_id = ?", (user_id,))
    money = cursor.fetchone()
    conn.close()
    return money[0]
    
async def get_country(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT country FROM users WHERE user_id = ?", (user_id,))
    country = cursor.fetchone()
    conn.close()
    return country[0]

async def get_country_params(country):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT economy, population, happiness, temp_rost FROM countries WHERE name = ?", (country,))
    country_params = cursor.fetchone()
    conn.close()
    return country_params

async def chek_is_admin(user_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins WHERE user_id =?", (user_id,))
    admin = cursor.fetchone()
    if admin:
        return True
    else:
        return False
    conn.close()
    
async def ban_user(user_id, admin_id):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM admins WHERE user_id =?", (user_id,))
        logging.info(f"Пользователь с ID: {user_id} был забанен админом с ID: {admin_id}")
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨Ошибка: " + str(e))
        return False
    conn.commit()
    conn.close()
    return True

async def broadcast_message(message_text):
    users = await get_all_users()
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
        except TelegramBadRequest as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")
            
async def get_all_users():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, country, role, money FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# endregion

# region admin

class RegisterAdmin(StatesGroup):
    password = State()

@r.message(Command("register_admin"))
async def register_admin(message: Message, state: FSMContext):
    await message.reply("🔑Введите пороль для аутентификации: ")
    await state.set_state(RegisterAdmin.password)
    
@r.message(RegisterAdmin.password)
async def register_admin_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await message.reply("✅Пароль аутентификации успешно введен.\nВведите команду /admin для познания команд админа")
        logging.info(F"Добавлен админ с ID: {message.from_user.id}")
        await add_admin(message.from_user.id)
        await state.clear()
        return
    else:
        await message.reply("🚨Неверный пароль. Попробуйте снова.")
        await state.clear()
        
@r.message(Command("admin"))
async def admin_command(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        return
    await message.answer("ban 'ID' - бан игрока по ID\ngivement 'sum' 'ID' - Выдача денег по ID\ncreate_country 'name' 'economy' 'population' 'happiness' 'temp_rost' - создание страны с добавление ее пораметров\ndelete_country 'name' - удаление страны по названию\nget_users - получение всех пользователей с их ID и вообщем все информации\nget_country - получени всех стран с их параметрами", reply_markup=keyboard_admin)
    
@r.message(Command("ban"))
async def ban_user(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался забанить игрока")
        return
    args = message.text.split()
    if len(args)!= 2:
        await message.reply("🚨Неверный формат команды. Используйте: /ban 'ID'", reply_markup=keyboard_admin)
        return
    user_id = int(args[1])
    if user_id == admin:
        ban_user(message.from_user.id, admin)
        logging.info(F"Пользователь с ID: {message.from_user.id} пытался забанить разработчика!")
    await ban_user(user_id, message.from_user.id)
    await message.reply(F"❗️Пользователь с ID: {user_id} был забанен", reply_markup=keyboard_admin)
    
@r.message(Command('givement'))
async def givement_pol(message: Message):
    connection = sqlite3.connect("game.db")
    cursor = connection.cursor()

    try:
        args = message.text.split()
        if len(args) < 3:
            raise ValueError("Неверный формат команды. Используйте: /givement <id получателя> <сумма> Пример /givement id пользователя 100", reply_markup=keyboard_admin)

        receiver_id = int(args[1])
        amount = float(args[2])

        cursor.execute("SELECT money FROM users WHERE user_id = ?", (message.from_user.id,))
        sender_cash = cursor.fetchone()

        if sender_cash is None:
            raise ValueError("Пользователь-отправитель не найден", reply_markup=keyboard_admin)
        
        if sender_cash[0] < amount:
            raise ValueError("Недостаточно средств для перевода", reply_markup=keyboard_admin)

        cursor.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, receiver_id))

        await bot.send_message(receiver_id, f'Вам начислено {amount}')
        
        logging.info(F"Перевод был исполнен админом с ID: {message.from_user.id} пользователь с ID: {receiver_id} на число {amount} денег", reply_markup=keyboard_admin)

        connection.commit()
        await message.reply("Перевод выполнен успешно", reply_markup=keyboard_admin)

    except Exception as e:
        connection.rollback()
        await message.reply(f"Ошибка: {e}")
        
class BroadcastForm(StatesGroup):
    waiting_for_message = State()
            
@r.message(Command("mailing"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id == admin or admin2:
        await message.answer("Введите сообщение для рассылки:", reply_markup=keyboard_admin)
        await state.set_state(BroadcastForm.waiting_for_message)
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")
    
@r.message(BroadcastForm.waiting_for_message, F.content_type == ContentType.TEXT)
async def get_broadcast_message(message: Message, state: FSMContext):
    broadcast_text = message.text

    await broadcast_message(broadcast_text)
    
    await message.answer("Рассылка завершена.", reply_markup=keyboard_admin)
    await state.clear()
    
@r.message(Command("get_users"))
async def get_users(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался получить список пользователей")
        return
    useri = await get_all_users()
    if useri:
        response = "список всех пользователей:\n"
        for user_id, name, money, country, role in useri:
            response += f"user_id - {user_id}, name - {name}, country - {money}, roleget - {country}, money- {role}\n"
    await message.reply(f"{response}")

    
# endregion