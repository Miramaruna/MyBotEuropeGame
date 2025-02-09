# region imports

import sqlite3, random, time, asyncio, logging, math


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

# region config
r = Router()
fm_t = False
Pop_t = False
chat_id = None
admin = 5626265763 
kol_kop = None
user_states = {}
user_states2 = {}
party_state = {}
party_t = False

# endregion

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
    is_user = await chek_is_user(message.from_user.id)
    money = await get_money(message.from_user.id)
    country = await get_country_from_users(message.from_user.id)
    if is_user == False:
        await message.reply("❌ Вы не зарегистрированы.")
        return
    try:
        if money < int(message.text):
            await message.reply("⚠ У вас недостаточно средств для инвестирования.")
            return
        try:
            await transfer_money(int(message.text), message.from_user.id, False)
            asyncio.create_task(invest_task(country, int(message.text), message.from_user.id))
            await message.reply("💼 Инвестирование начато. Вы будете получать прибыль каждые 20 секунд.")
            await state.clear()
        except BaseException as e:
            await message.reply("🚨 Ошибка: " + str(e))
            Invest = False
            await state.clear()
            return
    except BaseException as e:
        await message.reply("� Ошибка: " + str(e))
        Invest = False
        await state.clear()
        conn.commit()
        return

# endregion
    
# region earn money and product

@r.message(F.text.in_({"копать", "Копать", "rjgfnm", "Rjgfnm"}))
async def kop(message: Message):
    global kol_kop
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
    
    if user_id in user_states and user_states[user_id] == "blocked":
        await callback_query.answer("Производство уже запущено. Для начала нового производства нужно остановить текущее.")
        return
    
    user_states[user_id] = "blocked"
    
    await callback_query.answer("🏭 Производство начато.\n⏳Каждую минуту вы будете получать свой доход.")
    fm_t = True
    asyncio.create_task(start_production_activate(chat_id, user_id))
        
@r.callback_query(F.data == "stop_production")
async def stop_production(callback_query: types.CallbackQuery):
    global fm_t
    await callback_query.answer("🛑 Производство остановлено.")
    fm_t = False
    user_id = callback_query.from_user.id
    
    if user_id not in user_states or user_states[user_id] != "blocked":
        await callback_query.answer("Производство не было запущено.")
        return
    user_states[user_id] = "unblocked"
    
@r.callback_query(F.data == "start_population")
async def start_population(callback_query: types.CallbackQuery):
    global pop_t
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    is_user = await chek_is_user(user_id)
    if is_user == False:
        await callback_query.answer("❌ Вы не зарегистрированы.")
        fm_t = False
        return
    
    if user_id in user_states2 and user_states2[user_id] == "blocked":
        await callback_query.answer("Раздача товаров уже запущена. Для начала нового производства нужно остановить текущее.")
        return
    
    user_states2[user_id] = "blocked"
    
    await callback_query.answer("🎁 Раздача товаров начата.\n⏳Каждую минуту вы будете получать свой доход.")
    pop_t = True
    asyncio.create_task(start_population_activate(chat_id, user_id))
    
@r.callback_query(F.data == "stop_population")
async def stop_population(callback_query: types.CallbackQuery):
    global pop_t
    await callback_query.answer("🛑 Раздача товаров остановлена.")
    pop_t = False
    user_id = callback_query.from_user.id
    
    if user_id not in user_states2 or user_states2[user_id] != "blocked":
        await callback_query.answer("Раздача товаров не была запущена.")
        return
    user_states2[user_id] = "unblocked"
    
class Party(StatesGroup):
    amount = State()
    
@r.callback_query(F.data == "start_party_happy")
async def start_party(callback_query: CallbackQuery, state: FSMContext):
    global party_t
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    is_user = await chek_is_user(user_id)
    if is_user == False:
        await callback_query.answer("❌ Вы не зарегистрированы.")
        party_t = False
        return
    
    if user_id in user_states2 and user_states2[user_id] == "blocked":
        await callback_query.answer("Праздник уже начат. Подождите 7 минут до окончания праздника")
        return
    
    party_state[user_id] = "blocked"
    
    await callback_query.message.answer("Введите сумму которую потратите на праздник: ")
    await state.set_state(Party.amount)
    
@r.message(Party.amount)
async def party_accept_procces(message: Message, state: FSMContext):
    global party_t
    user_id = message.from_user.id
    chat_id = message.chat.id
    is_user = await chek_is_user(user_id)
    
    if is_user == False:
        await message.reply("❌ Вы не зарегистрированы.")
        party_t = False
        return
    
    money = await get_money(message.from_user.id)
    country = await get_country_from_users(message.from_user.id)
    try:
        if money < int(message.text):
            await message.reply("⚠ У вас недостаточно средств для праздника.")
            return
        if int(message.text) <= 500:
            await message.reply("Ваше население взбушевалось из-за маленького праздника -10 счастья")
            await transfer_happiness(10, country, False)
            return
            
        try:
            await transfer_money(int(message.text), message.from_user.id, False)
            asyncio.create_task(start_party_activate(chat_id, user_id, country, int(message.text)))
            await message.reply("Праздник начато. Вы будете получать отчет о празднике каждые 30 секунд.")
            party_t = True
            await state.clear()
        except BaseException as e:
            await message.reply("🚨 Ошибка: " + str(e))
            party_t = False
            await state.clear()
            return
    except BaseException as e:
        await message.reply("🚨 Ошибка: " + str(e))
        party_t = False
        await state.clear()
        conn.commit()
        return
    
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

async def start_party_activate(chat_id, user_id, country, money):
    global party_t
    numOfParty = 0
    numOfParty += 1
    params = await get_country_params(country)
    happiness_min = math.ceil(money / 2000)
    happiness_max = math.ceil(money / 500)
    party_t = True
    await transfer_happiness(30, country, False)
    
    if numOfParty >= 8:
        await bot.send_message(chat_id=chat_id, text="Праздник закончился!")
        party_t = False
        party_state[user_id] = "unblocked"
        return
    
    if params[3] >= 100:
            await bot.send_message(chat_id=chat_id, text="🎉 Счастье достигло 100! Праздник завершен.")
            party_t = False
            party_state[user_id] = "unblocked"
            return

    while party_t:
        current_happiness = await get_country_params(country)
        
        if current_happiness[3] >= 100:
            await bot.send_message(chat_id=chat_id, text="🎉 Счастье достигло 100! Праздник завершен.")
            party_t = False
            party_state[user_id] = "unblocked"
            break

        happiness = random.randint(happiness_min, happiness_max)

        await bot.send_message(chat_id=chat_id, text=f"📈 Счастье увеличилось на {happiness}.")
        await transfer_happiness(happiness, country, True)  # Обновляем значение в БД
        await asyncio.sleep(5)

async def invest_task(country, money, chat_id):
    Invest = True
    numOfInvest = 0
    economy_min = money // 10
    economy_max = money // 5
    while Invest:
        numOfInvest += 1
        economy = random.randint(economy_min, economy_max)
        if numOfInvest == 6:
            Invest = False
            break
        try:
            cursor.execute("UPDATE countries SET economy = economy + ? WHERE name = ?", (economy, country))
            await bot.send_message(chat_id=chat_id, text=f"✅ Было получено {economy} единиц экономики вашей страны.")
        except BaseException as e:
            await bot.send_message(chat_id=chat_id, text="🚨 Ошибка: " + str(e))
            Invest = False
            break
        await asyncio.sleep(20)

async def start_production_activate(chat_id, user_id):
    global pop_t

    # Вычисления для максимальных и минимальных доходов
    def calculate_income_params(params):
        economy_max = params[1] // 45
        population_max = params[2] // 30
        happiness_max = params[3] // 24
        income_max = economy_max + population_max * happiness_max

        econome_min = params[1] // 80
        population_min = params[2] // 50
        happiness_min = params[3] // 48
        income_min = econome_min + population_min * happiness_min

        return income_min, income_max

    # Основной цикл
    while fm_t:
        country = await get_country_from_users(user_id)
        params = await get_country_params(country)

        # Проверка валидности данных
        if not params or len(params) < 4:
            logging.error(f"Invalid params for country {country}: {params}")
            await asyncio.sleep(5)  # Пауза перед следующим циклом
            continue

        income_min, income_max = calculate_income_params(params)
        income = random.randint(income_min, income_max)
        
        await transfer_money(income, user_id, True)
        await bot.send_message(chat_id=chat_id, text=f"💰 Было получено {income} монет из страны {country}.")
        await asyncio.sleep(5)

async def start_population_activate(chat_id, user_id):
    global pop_t
    while pop_t:
        country = await get_country_from_users(user_id)
        params = await get_country_params(country)
        population_max = params[2] // 50 + params[4] // 5
        population_min = params[2] // 100 + params[4] // 15
        population = random.randint(population_min, population_max)
        
        await transfer_population(population, country, True)
        await bot.send_message(chat_id=chat_id, text=f"👩‍🍼 Было рождено {population} людей из страны {country}.")
        await asyncio.sleep(5)

async def add_admin(user_id):
    try:
        cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="❗️Ошибка: " + str(e))
        return False
    conn.commit()
    return True

async def transfer_population(population, country, is_positive):
    try:
        if is_positive:
            cursor.execute("UPDATE countries SET population = population + ? WHERE name =?", (population, country))
        else:
            cursor.execute("UPDATE countries SET population = population - ? WHERE name =?", (population, country))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨 Ошибка: " + str(e))
        return False
    conn.commit()
    return True

async def transfer_happiness(happiness, country, is_positive):
    try:
        if is_positive:
            cursor.execute("UPDATE countries SET happiness = happiness + ? WHERE name =?", (happiness, country))
        else:
            cursor.execute("UPDATE countries SET happiness = happiness - ? WHERE name =?", (happiness, country))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨 Ошибка: " + str(e))
        return False
    conn.commit()
    return True

async def transfer_money(money, user_id, is_positive):
    try:
        if is_positive == True:
            cursor.execute("UPDATE users SET money = money + ? WHERE user_id =?", (money, user_id))
        else:
            cursor.execute("UPDATE users SET money = money - ? WHERE user_id =?", (money, user_id))
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨 Ошибка: " + str(e))
        return False
    conn.commit()
    return True
    
async def chek_is_user(user_id):
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False
    
async def get_money(user_id):
    cursor.execute("SELECT money FROM users WHERE user_id = ?", (user_id,))
    money = cursor.fetchone()
    return money[0]
    
async def get_country_from_users(user_id):
    cursor.execute("SELECT country FROM users WHERE user_id = ?", (user_id,))
    country = cursor.fetchone()
    return country[0]

async def get_country_params(country):
    cursor.execute("SELECT capital, economy, population, happiness, temp_rost FROM countries WHERE name = ?", (country,))
    country_params = cursor.fetchone()
    return country_params

async def chek_is_admin(user_id):
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
    admin = cursor.fetchone()
    if admin is None:
       return  False
    elif admin is not None:
        return True
    else:
        return False
    
async def ban_user(user_id, admin_id):
    try:
        cursor.execute("DELETE FROM admins WHERE user_id =?", (user_id,))
        logging.info(f"Пользователь с ID: {user_id} был забанен админом с ID: {admin_id}")
    except BaseException as e:
        await bot.send_message(chat_id=admin, text="🚨Ошибка: " + str(e))
        return False
    conn.commit()
    return True
            
async def get_all_users():
    cursor.execute("SELECT user_id, name, country, role, money FROM users")
    users = cursor.fetchall()
    return users

async def get_all_users_id():
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    return [user[0] for user in users]

async def get_user_params(user_id):
    cursor.execute("SELECT name, country, role, money FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    return user

async def broadcast_message(message_text):
    users = await get_all_users_id()
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=str(message_text))
        except TelegramBadRequest as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")
            
async def get_all_country_params():
    cursor.execute("SELECT capital, name, economy, population, happiness, temp_rost FROM countries")
    countries = cursor.fetchall()
    return countries

# endregion

# region admin

class RegisterAdmin(StatesGroup):
    password = State()

@r.message(Command("register_admin"))
async def register_admin(message: Message, state: FSMContext):
    await message.reply("🔑Введите пороль для аутентификации: \nОтмена - отмена")
    await state.set_state(RegisterAdmin.password)
    
@r.message(RegisterAdmin.password)
async def register_admin_password(message: Message, state: FSMContext):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == True:
        await message.reply("🚨Вы уже администратор.")
        await state.clear()
        return
    if message.text == "Отмена" or message.text == "отмена":
        await message.reply("Отмена регистрации.")
        await state.clear()
        return
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
    try:
        args = message.text.split()
        if len(args) < 3:
            raise ValueError("Неверный формат команды. Используйте: /givement <id получателя> <сумма>. Пример: /givement <id пользователя> 100")

        receiver_id = int(args[1])
        amount = float(args[2])

        cursor.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, receiver_id))

        await bot.send_message(receiver_id, f'Вам начислено {amount}')
        
        logging.info(f"Перевод был исполнен админом с ID: {message.from_user.id} пользователю с ID: {receiver_id} на сумму {amount} денег")

        conn.commit()
        await message.reply("Перевод выполнен успешно", reply_markup=keyboard_admin)

    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}", reply_markup=keyboard_admin)
    except Exception as e:
        conn.rollback()
        await message.reply(f"Ошибка: {e}")

        
class BroadcastForm(StatesGroup):
    waiting_for_message = State()
            
@r.message(Command("mailing"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id == admin or admin2:
        await message.answer("Введите сообщение для рассылки:\n🚨Отмена - отмена", reply_markup=keyboard_admin)
        await state.set_state(BroadcastForm.waiting_for_message)
    else:
        await message.answer("🚨У вас нет прав для выполнения этой команды.")
    
@r.message(BroadcastForm.waiting_for_message, F.content_type == ContentType.TEXT)
async def get_broadcast_message(message: Message, state: FSMContext):
    broadcast_text = message.text
    
    if broadcast_text == "отмена" or broadcast_text == "Отмена":
        await message.answer("Рассылка отменена.", reply_markup=keyboard_admin)
        await state.clear()
        return

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
            response += f"user_id - {user_id}, name - {name}, country - {money}, role - {country}, money- {role}\n"
    await message.reply(f"{response}")
    
@r.message(Command("get_country"))
async def get_country(message: Message):
    user_id = message.from_user.id
    countries = await get_all_country_params()
    is_admin = await chek_is_admin(user_id)
    if is_admin == False:
        await message.reply("У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался получить список стран")
        return
    if countries:
        response = "список всех стран:\n"
        for capital, name, economy, population, happiness, temp_rost in countries:
            response += f"capital - {capital}, name - {name}, economy - {economy}, population - {population}, happiness - {happiness}, temp_rost - {temp_rost}\n"
    await message.reply(f"{response}")

@r.message(Command("delete_country"))
async def delete_country(message: Message):
    try:
        args = message.text.split()
        if len(args)!= 2:
            raise ValueError("Неверный формат команды. Используйте: /delete_country <название страны>")

        name = args[1]

        cursor.execute("DELETE FROM countries WHERE name = ?", (name,))

        conn.commit()
        await message.reply(f"Страна '{name}' успешно удалена.", reply_markup=keyboard_admin)
    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}", reply_markup=keyboard_admin)
           
@r.message(Command("create_country"))
async def create_country(message: Message):

    try:
        args = message.text.split()
        if len(args)!= 6:
            raise ValueError("Неверный формат команды. Используйте: /create_country <название страны> <экономика> <население> <счастье> <темп роста>")

        name = args[1]
        economy = args[2]
        population = args[3]
        happiness = args[4]
        temp_rost = args[5]

        cursor.execute("INSERT INTO countries (name, economy, population, happiness, temp_rost) VALUES (?,?,?,?,?)", (name, economy, population, happiness, temp_rost))
        await message.reply(f"Страна '{name}' успешно создана.", reply_markup=keyboard_admin)

        conn.commit()
    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}", reply_markup=keyboard_admin)
    
# endregion