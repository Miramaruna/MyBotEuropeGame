# region imports

import sqlite3, random, time, asyncio, logging, math
from aiogram import F, Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery, BotCommand, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram import types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ContentType, ChatMemberUpdated
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import FSInputFile
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

# region States

class Party(StatesGroup):
    amount = State()
    
class RegisterAdmin(StatesGroup):
    password = State()
    
class BroadcastForm(StatesGroup):
    waiting_for_message = State()
    
class Investigate(StatesGroup):
    num = State()

# endregion

# region Need methods

async def set_happy_max(country):
    cursor.execute("UPDATE countries SET happiness = 100 WHERE name = ?", country)
    conn.commit()
    return

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
            await set_happy_max(country)
            return

    while party_t:
        current_happiness = await get_country_params(country)
        
        if current_happiness[3] >= 100:
            await bot.send_message(chat_id=chat_id, text="🎉 Счастье достигло 100! Праздник завершен.")
            party_t = False
            party_state[user_id] = "unblocked"
            await set_happy_max(country)
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
    users = await get_all_users()  # Assuming you have a function to get all user IDs
    for user in users:
        user_id = user[0]
        try:
            await bot.send_message(chat_id=user_id, text=str(message_text))
        except TelegramForbiddenError:
            print(f"Cannot send message to user {user_id}: This user is a bot")
        except Exception as e:  
            print(f"Error sending message to user {user_id}: {str(e)}")
            
async def get_all_country_params():
    cursor.execute("SELECT capital, name, economy, population, happiness, temp_rost FROM countries")
    countries = cursor.fetchall()
    return countries

async def add_army_tanks(id, price, number):
    cursor.execute("UPDATE army SET tanks = tanks + ? WHERE user_id = ?", (number, id))
    await transfer_money(price, id, False)
    conn.commit()

def get_army(user_id):
    cursor.execute('SELECT soldiers, cars, tanks FROM army WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return {'soldiers': result[0], 'cars': result[1], 'tanks': result[2]} if result else None

def calculate_army_strength(army):
    soldiers = army['soldiers']
    cars = army['cars']
    tanks = army['tanks']
    
    needed_soldiers_for_cars = cars * 3
    needed_soldiers_for_tanks = tanks * 4
    total_needed_soldiers = needed_soldiers_for_cars + needed_soldiers_for_tanks
    
    if soldiers < total_needed_soldiers:
        return None 
    
    remaining_soldiers = soldiers - total_needed_soldiers
    strength = remaining_soldiers + (cars * 5) + (tanks * 20)
    return strength

async def army_accept(id, price):
    cursor.execute(f"SELECT money FROM users WHERE user_id = {id}")
    c = cursor.fetchone()
    money = c[0]
    if money >= price:
        return True
    else: 
        return False
    
async def add_army_slodiers(id, price, number):
    country = await get_country_from_users(id)
    params = await get_country_params(country)
    happiness = params[3]
    population = params[3]
    counter_happiness = math.ceil(happiness / 1000)
    if population < 100:
        await bot.send_message(chat_id=id, text=f"У вашего населения меньше 100\nВаше актуальное население: {population}")
        return
    if population < number:
        await bot.send_message(chat_id=id, text=f"У вашего населения меньше чем вы хотите за вербовать: {number}\nВаше население: {population}")
        return
    if happiness < 20:
        await bot.send_message(chat_id=id, text=f"У ваше счастье меньше 20\nВаше актуальное счастье: {happiness}")
        return
    if counter_happiness > happiness:
        await bot.send_message(chat_id=id, text=f"Вы слишком много вербуете солдатов население в недовольствие!")
        return
    cursor.execute("UPDATE army SET soldiers = soldiers + ? WHERE user_id = ?", (number, id))
    await transfer_happiness(counter_happiness, country, False)
    await transfer_population(number, country, False)
    await transfer_money(price, id, False)
    conn.commit()
    
async def add_army_cars(id, price, number):
    cursor.execute("UPDATE army SET cars = cars + ? WHERE user_id = ?", (number, id))
    await transfer_money(price, id, False)
    conn.commit()
    
async def chek_is_war(attacker_id, defender_id):
    cursor.execute(f"SELECT * FROM wars WHERE (country1 = {attacker_id} AND country2 = {defender_id}) OR (country1 = {defender_id} AND country2 = {attacker_id})")
    result = cursor.fetchone()
    if result is not None:
        return True
    else:
        return False
    
async def chek_is_army(user_id):
    cursor.execute(f"SELECT * FROM army WHERE user_id = {user_id}")
    result = cursor.fetchone()
    if result is not None:
        return True
    else:
        return False
    
def get_population_tier_list():
    """ Получение тир-листа стран по населению (ТОП-5) """
    cursor.execute("SELECT name, population FROM countries ORDER BY population DESC LIMIT 5")
    top_countries = cursor.fetchall()
    
    if not top_countries:
        return "📊 **Тир-лист по населению пуст**"

    tier_list = "📊 **Тир-лист по населению:**\n"
    for idx, (country, population) in enumerate(top_countries, 1):
        tier_list += f"{idx}. {country} — {population} 👥\n"
    
    return tier_list

def get_army(user_id):
    """ Получение армии пользователя из БД """
    cursor.execute("SELECT soldiers, cars, tanks FROM army WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return {'soldiers': result[0], 'cars': result[1], 'tanks': result[2]} if result else None

def update_army(user_id, soldiers, cars, tanks):
    """ Обновление армии в БД """
    cursor.execute("""
        UPDATE army SET soldiers = ?, cars = ?, tanks = ? WHERE user_id = ?
    """, (max(0, soldiers), max(0, cars), max(0, tanks), user_id))
    conn.commit()

def check_war_status(user_1_id, user_2_id):
    """ Проверка, находятся ли игроки в войне и не в перемирии """
    cursor.execute("""
        SELECT result FROM wars WHERE 
        (country1 = ? AND country2 = ?) OR (country1 = ? AND country2 = ?)
    """, (user_1_id, user_2_id, user_2_id, user_1_id))
    
    war = cursor.fetchone()
    return war and war[0] == "active"  # Если статус "active", значит идет война

def calculate_army_strength(army):
    """ Вычисление силы армии """
    soldiers, cars, tanks = army['soldiers'], army['cars'], army['tanks']
    needed_soldiers = (cars * 3) + (tanks * 4)

    if soldiers < needed_soldiers:
        return None  # Недостаточно солдат для управления техникой

    return (soldiers - needed_soldiers) + (cars * 5) + (tanks * 20)

# endregion

# region InCountryMethods

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
    
# endregion
    
# region guest methods

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
    
@r.message(Command("map"))
async def show_map(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть карту", web_app=WebAppInfo(url="https://www.flickr.com/photos/202286975@N06/54326715216/in/dateposted-public/"))]
        ]
    )
    
    await message.answer("Нажми кнопку, чтобы открыть карту:", reply_markup=keyboard)
    
@r.message(F.text.startswith('дать'))
async def give_currency(message: Message):
    if not message.reply_to_message:
        await message.reply("Вы должны ответить на сообщение пользователя, чтобы передать валюту.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("Вы должны указать сумму. Пример: дать 100")
            return
        
        amount = int(parts[1])

        if amount <= 0:
            await message.reply("Сумма должна быть положительной.")
            return

    except ValueError:
        await message.reply("Некорректная сумма. Пример: дать 100")
        return

    from_user_id = message.from_user.id
    to_user_id = message.reply_to_message.from_user.id


    cursor.execute(F"SELECT money FROM users WHERE user_id = {message.from_user.id}")
    c = cursor.fetchone()
    money = c[0]
    if money < amount:
        await message.reply("У вас недостаточно средств.")
    
@r.message(Command("list_economy"))
async def show_tierlist(message: types.Message):
    cursor.execute("SELECT name, economy FROM countries ORDER BY economy DESC")
    economy_list = cursor.fetchall()

    if not economy_list:
        await message.answer("⚠ Данные отсутствуют.")
        return

    tier_list = "\n".join([f"🏆 {i+1}. {name} - {economy}💰" for i, (name, economy) in enumerate(economy_list)])

    await message.answer(f"📊 **Тир-лист экономики**:\n{tier_list}")

@r.message(Command("list_population"))
async def list_population(message: Message):
    """ Команда для вывода тир-листа стран по населению """
    tier_list = get_population_tier_list()
    await message.answer(tier_list)
    
# endregion 

# region Army

@r.message(F.text.lower() == 'сражаться')
async def battle(message: Message):
    """ Логика сражения между двумя пользователями """
    if not message.reply_to_message:
        await message.answer("⚔️ **Сражение возможно только в ответ на сообщение соперника!**")
        return

    user_1_id, user_2_id = message.from_user.id, message.reply_to_message.from_user.id

    # Проверяем, находятся ли они в войне и не в перемирии
    if not check_war_status(user_1_id, user_2_id):
        await message.answer("❌ **Вы не находитесь в войне или у вас перемирие!**")
        return

    army_1, army_2 = get_army(user_1_id), get_army(user_2_id)

    if not army_1 or not army_2:
        await message.answer("❌ **Не удалось найти армию одного из пользователей.**")
        return

    strength_1, strength_2 = calculate_army_strength(army_1), calculate_army_strength(army_2)

    # Если у первой армии не хватает солдат → сразу проигрыш
    if strength_1 is None:
        await message.answer(f"⚠ **{message.from_user.username} проиграл! Недостаточно солдат для управления техникой.** ❌")
        update_army(user_1_id, army_1['soldiers'] // 2, army_1['cars'] // 2, army_1['tanks'] // 2)
        return
    
    # Если у второй армии не хватает солдат → сразу проигрыш
    if strength_2 is None:
        await message.answer(f"⚠ **{message.reply_to_message.from_user.username} проиграл! Недостаточно солдат для управления техникой.** ❌")
        update_army(user_2_id, army_2['soldiers'] // 2, army_2['cars'] // 2, army_2['tanks'] // 2)
        return

    # Победа первой армии
    if strength_1 > strength_2:
        result_message = f"🏆 **Победитель:** {message.from_user.username}!\n💥 **Сила армии:** {strength_1} vs {strength_2}"
        
        # Уменьшаем армию победителя на 20% от проигравшего
        update_army(
            user_1_id,
            army_1['soldiers'] - int(army_2['soldiers'] * 0.2),
            army_1['cars'] - int(army_2['cars'] * 0.2),
            army_1['tanks'] - int(army_2['tanks'] * 0.2)
        )
        
        # Проигравший теряет 90%
        update_army(
            user_2_id,
            int(army_2['soldiers'] * 0.1),
            int(army_2['cars'] * 0.1),
            int(army_2['tanks'] * 0.1)
        )

    # Победа второй армии
    elif strength_1 < strength_2:
        result_message = f"🏆 **Победитель:** {message.reply_to_message.from_user.username}!\n💥 **Сила армии:** {strength_2} vs {strength_1}"
        
        # Уменьшаем армию победителя на 20% от проигравшего
        update_army(
            user_2_id,
            army_2['soldiers'] - int(army_1['soldiers'] * 0.2),
            army_2['cars'] - int(army_1['cars'] * 0.2),
            army_2['tanks'] - int(army_1['tanks'] * 0.2)
        )
        
        # Проигравший теряет 90%
        update_army(
            user_1_id,
            int(army_1['soldiers'] * 0.1),
            int(army_1['cars'] * 0.1),
            int(army_1['tanks'] * 0.1)
        )

    # Ничья → обе армии теряют от 10% до 15%
    else:
        percent_1 = random.randint(10, 15) / 100
        percent_2 = random.randint(10, 15) / 100
        result_message = f"⚔ **Ничья!** Обе армии потеряли силы.\n💪 Сила армии: {strength_1} vs {strength_2}"

        update_army(
            user_1_id,
            int(army_1['soldiers'] * (1 - percent_1)),
            int(army_1['cars'] * (1 - percent_1)),
            int(army_1['tanks'] * (1 - percent_1))
        )

        update_army(
            user_2_id,
            int(army_2['soldiers'] * (1 - percent_2)),
            int(army_2['cars'] * (1 - percent_2)),
            int(army_2['tanks'] * (1 - percent_2))
        )

    await message.answer(result_message)

@r.message(F.text.in_({'Армия','армия','Army'}))
async def army(message: Message):
    cursor.execute(F"SELECT user_id FROM army WHERE user_id = {message.from_user.id}")
    u = cursor.fetchone()
    conn.commit
    if u == None:
        cursor.execute("INSERT INTO army(user_id, soldiers, cars, tanks) VALUES(?, ?, ?, ?)", (message.from_user.id, 10, 2, 1))
        conn.commit()
        await message.answer("Армия создана!🪖")
    else:
        cursor.execute(f"SELECT soldiers FROM army WHERE user_id = {message.from_user.id}")
        s = cursor.fetchone()
        soldiers = s[0]
        cursor.execute(f"SELECT cars FROM army WHERE user_id = {message.from_user.id}")
        c = cursor.fetchone()
        cars = c[0]
        cursor.execute(f"SELECT tanks FROM army WHERE user_id = {message.from_user.id}")
        t = cursor.fetchone()
        tanks = t[0]
        conn.commit()
        balls = soldiers + (cars * 5) + (tanks * 20)
        need = (cars * 3) + (tanks * 4)
        if soldiers <= need:
            await message.answer(f"Не хватка Солдат!{soldiers - need}", reply_markup=armmy_kb)
        else:
            await message.answer(f"--Армия--\nСолдаты - {soldiers - need}🪖\nМашины - {cars}🛻\nТанки - {tanks}💥\nБаллы - {balls}\nДля познания команд отношении введите - /army_peace", reply_markup=armmy_kb)

@r.message(Command("army_peace"))
async def army_peace_help(message: Message):
    await message.answer("Команды для отношении:\nОбьявить войну - надо ответить на сообщение собеседника\nОбьявить перемирие - надо ответить на сообщение собеседника и быть в войне с ним\nсражаться - надо ответить на сообщение быть в состояние войны также быть в нужной тактике и иметь превосходство либо подобрать тактику которую вы будете использовать чтоб победить в сражении", reply_markup=keyboard_army_peace)

@r.callback_query(F.data == 'sol')
async def add_soldiers(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 100)
    if acc == True:
        await add_army_slodiers(callback.from_user.id, 100, 10)
        await callback.message.answer("10 Солдат успешно прибыли в вашу армию!🪖")
    else:
        await callback.message.answer("Не достаточно денег📉")

@r.callback_query(F.data == 'car')
async def add_сars(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 1000)
    if acc == True:
        await add_army_cars(callback.from_user.id, 1000, 5)
        await callback.message.answer("5 Машин успешно прибыли в вашу армию!🪖")
    else:
        await callback.message.answer("Не достаточно денег📉")

@r.callback_query(F.data == 'tan')
async def add_tanks(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 3000)
    if acc == True:
        await add_army_tanks(callback.from_user.id, 3000, 1)
        await callback.message.answer("1 Танк успешно прибыли в вашу армию!🪖")
    else:
        await callback.message.answer("Не достаточно денег📉")

# Обработчик ответа на сообщение с объявлением войны
@r.message(F.text == "обьявить войну")
async def declare_war(message: types.Message, state: FSMContext):
    if message.reply_to_message:  # Проверяем, что это ответ на сообщение
        attacker_id = message.from_user.id  # ID того, кто объявляет войну
        defender_id = message.reply_to_message.from_user.id  # ID того, кому объявляют войну
        
        is_user1 = await chek_is_user(attacker_id)
        is_user2 = await chek_is_user(defender_id)
        is_war = await chek_is_war(attacker_id, defender_id)
        is_army1 = await chek_is_army(attacker_id)
        is_army2 = await chek_is_army(defender_id)
        if is_user1 == False:
            await message.reply("Вы не зарегистрированы!")
            return
        if is_user2 == False:
            await message.reply("Враг не зарегистрирован!")
            return
        
        if is_war == True:
            await message.reply("Вы уже объявили войну с этим игроком!")
            return

        if is_army1 == False:
            await message.reply("Вы не создали армию!")
            return
        
        if is_army2 == False:
            await message.reply("Враг не создали армию!")
            return

        cursor.execute(
            "INSERT INTO wars (country1, country2, result) VALUES (?, ?, ?) ", (attacker_id, defender_id, "active"))
        conn.commit()

        await message.reply(f"⚔ Война объявлена против <b>{message.reply_to_message.from_user.full_name}</b>!", parse_mode="HTML")
        await bot.send_message(chat_id=defender_id, text=f"⚔ Вам обьявлена война против <b>{message.reply_to_message.from_user.full_name}</b>!", parse_mode="HTML")
    else:
        await message.reply("⚠ Чтобы объявить войну, ответьте на сообщение врага!")

@r.message(F.text == "обьявить перемирие")
async def propose_peace(message: types.Message):
    if message.reply_to_message:
        sender_id = message.from_user.id  # Кто предлагает мир
        receiver_id = message.reply_to_message.from_user.id  # Кому предлагают мир

        is_war = await chek_is_war(sender_id, receiver_id)
        
        if is_war == False:
            await message.reply("⚠ У вас нет активной войны с этим игроком!")

        # Записываем запрос на мир
        cursor.execute(
            "INSERT INTO peace_requests (sender_id, receiver_id, status) VALUES (?, ?, 'pending') "
            "ON CONFLICT(sender_id, receiver_id) DO UPDATE SET status = 'pending'",
            (sender_id, receiver_id)
        )

        buttons = [
            [InlineKeyboardButton(text="🤝 Принять мир", callback_data=f"accept_peace:{sender_id}")],
            [InlineKeyboardButton(text="❌ Отклонить мир", callback_data=f"decline_peace:{sender_id}")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.bot.send_message(
            chat_id=receiver_id,
            text=f"⚖ {message.from_user.full_name} предлагает вам мир. Примите или отклоните.",
            reply_markup=keyboard
        )
    else:
        await message.reply("⚠ Чтобы предложить мир, ответьте на сообщение врага!")
        
@r.callback_query(F.data.startswith("accept_peace:"))
async def accept_peace(callback_query: types.CallbackQuery):
    receiver_id = callback_query.from_user.id  # Кто принимает мир
    sender_id = int(callback_query.data.split(":")[1])  # Кто предложил мир

    # Проверяем, есть ли мирное предложение
    cursor.execute(
        "SELECT status FROM peace_requests WHERE sender_id = ? AND receiver_id = ?",
        (sender_id, receiver_id)
    )
    peace_request = cursor.fetchone()

    if not peace_request or peace_request[0] != "pending":
        await callback_query.answer("❌ У вас нет активного запроса на мир.")
        conn.close()
        return

    # Обновляем статус войны в таблице wars
    cursor.execute(
        "UPDATE wars SET result = 'peace' WHERE (country1 = ? AND country2 = ?) OR (country2 = ? AND country1 = ?)",
        (sender_id, receiver_id, receiver_id, sender_id)
    )

    # Удаляем запрос на мир
    cursor.execute(
        "DELETE FROM peace_requests WHERE sender_id = ? AND receiver_id = ?",
        (sender_id, receiver_id)
    )

    await callback_query.message.edit_text("✅ Мир заключён! Война окончена.")
    await callback_query.bot.send_message(sender_id, "✅ Ваше предложение о мире принято!")

@r.callback_query(F.data.startswith("decline_peace:"))
async def decline_peace(callback_query: types.CallbackQuery):
    receiver_id = callback_query.from_user.id
    sender_id = int(callback_query.data.split(":")[1])

    cursor.execute(
        "DELETE FROM peace_requests WHERE sender_id = ? AND receiver_id = ?",
        (sender_id, receiver_id)
    )

    await callback_query.message.edit_text("❌ Мир отклонён. Война продолжается.")
    await callback_query.bot.send_message(sender_id, "❌ Ваше предложение о мире было отклонено.")

        
# endregion

# region admin

@r.message(Command("register_admin"))
async def register_admin(message: Message, state: FSMContext):
    await message.reply("🔑Введите пороль для аутентификации: \nОтмена - отмена")
    await state.set_state(RegisterAdmin.password)
    
@r.message(RegisterAdmin.password)
async def register_admin_password(message: Message, state: FSMContext):
    if message.text == "Отмена" or message.text == "отмена":
        await message.reply("Отмена регистрации.")
        await state.finish()
        return
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.reply("Вы не зарегистрированы.")
        await state.clear()
        return
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
async def ban_user_message(message: Message):
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
        logging.info(F"Пользователь с ID: {message.from_user.id} пытался забанить разработчика!")
        return
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

        try:
            await bot.send_message(chat_id=receiver_id, text=f'Вам начислено {amount}')
        except TelegramForbiddenError:
            print(f"Cannot send message to user {receiver_id}: This user is a bot")
        
        logging.info(f"Перевод был исполнен админом с ID: {message.from_user.id} пользователю с ID: {receiver_id} на сумму {amount} денег")

        conn.commit()
        await message.reply("Перевод выполнен успешно", reply_markup=keyboard_admin)

    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}", reply_markup=keyboard_admin)
    except Exception as e:
        conn.rollback()
        await message.reply(f"Ошибка: {e}")
            
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
            raise ValueError("Неверный формат команды. Используйте: /create_country <столица> <название страны> <экономика> <население> <счастье> <темп роста>")

        capital = args[1]
        name = args[2]
        economy = args[3]
        population = args[4]
        happiness = args[5]
        temp_rost = args[6]

        cursor.execute("INSERT INTO countries (capital, name, economy, population, happiness, temp_rost) VALUES (?, ?,?,?,?,?)", (capital, name, economy, population, happiness, temp_rost))
        await message.reply(f"Страна '{name}' успешно создана.", reply_markup=keyboard_admin)

        conn.commit()
    except ValueError as ve:
        await message.reply(f"Ошибка: {ve}", reply_markup=keyboard_admin)
        
@r.message(Command("update_country"))
async def update_country(message: Message):
    try:
        args = message.text.split()
        if len(args)!= 7:
            raise ValueError("Неверный формат команды. Используйте: /update_country <название страны> <столица> <экономика> <население> <счастье> <темп роста>")
        chek_is_country = await get_country_params(args[1])
        if chek_is_country is None:
            await message.answer("Страна не найдена!")
            return

        name = args[1]
        capital = args[2]
        economy = args[3]
        population = args[4]
        happiness = args[5]
        temp_rost = args[6]

        cursor.execute("UPDATE countries SET capital =?, economy =?, population =?, happiness =?, temp_rost =? WHERE name =?", (capital, economy, population, happiness, temp_rost, name))
        conn.commit()
        await message.reply(f"Изменения в стране '{name}' успешно сохранены.", reply_markup=keyboard_admin)
    except Exception as e:
        await message.reply(f"Ошибка: {e}")
        conn.rollback()
        
@r.message(Command('ban_admin'))
async def ban_admin(message: Message, state:FSMContext):
    if message.from_user.id == admin:
        await message.answer("Введите ID админа для удаления🪪:")
        await state.set_state(Ban.id)
    else:
        await message.reply("У вас не доступа!❌")

    @r.message(Ban.id)
    async def ban_admin_True(message: Message, state: FSMContext):
        cursor.execute(f"SELECT user_id FROM admins WHERE user_id = {message.text}")
        a = cursor.fetchone()
        adma = a[0]
            
        if adma != None:
            cursor.execute(f"DELETE FROM admins WHERE user_id = {message.text}")
            connection.commit()
            await bot.send_message(message.text, f"Вы были удалены админом {message.from_user.first_name}")
            await message.reply("Удаление прошло успешно!✅")
            await state.clear()
        else:
            await message.answer("Такого админа нет🙅‍♂️")
    
# endregion