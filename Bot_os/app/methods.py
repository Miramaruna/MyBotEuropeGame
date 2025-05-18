from app.imports import *
from app.config import *
from bot import *
            
async def chek_is_ready(user_id):
    cursor.execute("SELECT ready FROM army WHERE user_id =?", (user_id,))
    ready_check = cursor.fetchone()
    if ready_check[0] < 100:
        return True
    elif ready_check[0] >= 100:
        return False
    else:
        return "error"

async def generate_captcha():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))  # Две случайные буквы (заглавные)
    numbers = ''.join(random.choices(string.digits, k=2))  # Две случайные цифры
    captcha = letters + numbers
    return captcha

async def set_happy_max(country):
    cursor.execute("UPDATE countries SET happiness = 100 WHERE name = ?", (country,))
    conn.commit()
    return

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
    cursor.execute("SELECT * FROM countries WHERE name = ?", (country,))
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
        cursor.execute("DELETE FROM users WHERE user_id =?", (user_id,))
        is_admin = await chek_is_admin(user_id)
        if is_admin == True:
            cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            logging.warning(f"Админ с ID: {user_id}, был забанен админом с ID: {admin_id}")
            if admin != user_id:
                await bot.send_message(user_id, "📇Ваша админка была снята!")
            if admin == user_id:
                await bot.send_message(admin_id, "↪️Вы успешно вышли из админского аккаунта")
        logging.warning(f"Пользователь с ID: {user_id} был забанен админом с ID: {admin_id}")
        if user_id != admin_id:
            await bot.send_message(user_id, "❗️Вы были забанены! админом")
        if user_id == admin_id:
            await bot.send_message(user_id, "↪️Вы успешно вышли из аккаунта!")
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

async def calculate_army_strength(army, country_name):
    soldiers = army['soldiers']
    cars = army['cars']
    tanks = army['tanks']
    
    # Получаем бонусы из параметров страны
    country = await get_country_params(country=country_name)
    if not country:
        return None  # или можно кинуть ошибку
    
    attack_bonus = country[10]  # Индекс атаки
    defense_bonus = country[9]  # Индекс защиты

    # Сколько нужно солдат для обслуживания техники
    needed_soldiers_for_cars = cars * 3
    needed_soldiers_for_tanks = tanks * 4
    total_needed_soldiers = needed_soldiers_for_cars + needed_soldiers_for_tanks

    # Остаток солдат, не занятых техникой
    remaining_soldiers = max(0, soldiers - total_needed_soldiers)

    # Расчёт базовой силы армии
    base_strength = remaining_soldiers + (cars * 5) + (tanks * 20)

    # Учитываем бонус атаки (например, 1.1 = +10%)
    # total_strength = base_strength * attack_bonus

    return {
        "strength": base_strength,
        "soldiers": soldiers,
        "cars": cars,
        "tanks": tanks,
        "needed_soldiers": total_needed_soldiers,
        "attack_bonus": attack_bonus,
        "defense_bonus": defense_bonus
    }

async def army_accept(id, price, number):
    country = await get_country_from_users(id)
    params = await get_country_params(country)
    cursor.execute(f"SELECT money FROM users WHERE user_id = {id}")
    population = params[3]
    happiness = params[4]
    counter_happiness = math.ceil(happiness / 1000 * (number / 1000))
    c = cursor.fetchone()
    money = c[0]
    if money >= price:
        return True
    if population < 100:
        await bot.send_message(chat_id=id, text=f"👥У вашего населения меньше 100\nВаше актуальное население: {population}")
        return False
    if population < number:
        await bot.send_message(chat_id=id, text=f"👥У вашего населения меньше чем вы хотите за вербовать: {number}\nВаше население: {population}")
        return False
    if happiness < 20:
        await bot.send_message(chat_id=id, text=f"😡У ваше счастье меньше 20\nВаше актуальное счастье: {happiness}")
        return False
    if counter_happiness > happiness:
        await bot.send_message(chat_id=id, text=f"😡Вы слишком много вербуете солдатов население в недовольствие!")
        return False
    return False
    
async def add_army_slodiers(id, price, number):
    country = await get_country_from_users(id)
    params = await get_country_params(country)
    happiness = params[4]
    population = params[3]
    counter_happiness = math.ceil(happiness / 1000)
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

async def get_army(user_id):
    """ Получение армии пользователя из БД """
    cursor.execute("SELECT soldiers, cars, tanks, tactic, ready FROM army WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return {'soldiers': result[0], 'cars': result[1], 'tanks': result[2], 'tactic': result[3], 'ready': result[4]} if result else None

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

async def edit_tactic(user_id, tactic):
    cursor.execute("UPDATE army SET tactic =? WHERE user_id =?", (tactic, user_id))
    conn.commit()
    return

async def get_tactics_by_user(user_id):
    cursor.execute("SELECT tactic FROM army WHERE user_id=?", (int(user_id),))
    tactic = cursor.fetchone()
    return tactic[0]

async def get_ready_army_by_user(user_id):
    try:
        cursor.execute("SELECT ready FROM army WHERE user_id = ?", (int(user_id),))
        ready = cursor.fetchone()
        return ready[0]
    except BaseException as e:
        print(f"[ERROR]:get_ready_army_by_user: user_id:{user_id}, Error:{e}")
    return

async def set_army_ready_by_user(user_id, amount):

def is_on_cooldown(user_id):
    cursor.execute("SELECT cooldown_until FROM battle_cooldowns WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0] > int(time.time())
    return False

def get_cooldown_time_left(user_id):
    cursor.execute("SELECT cooldown_until FROM battle_cooldowns WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return max(0, result[0] - int(time.time()))
    return 0

def set_cooldown(user_id):
    cooldown_until = int(time.time()) + COOLDOWN_SECONDS
    cursor.execute("""
        INSERT INTO battle_cooldowns (user_id, cooldown_until)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET cooldown_until=excluded.cooldown_until
    """, (user_id, cooldown_until))
    conn.commit()