from app.imports import *
from app.states import *
from app.config import *
from app.methods import *
from bot import *

# region​‌‌‍ ⁡⁢⁢⁣Need methods⁡​

async def while_transfer_ready_army(user_id, ready, call):
    global ready_army
    while ready_army:
        is_ready = await chek_is_ready(user_id)
        if is_ready is True:
            try:
                cursor.execute(
                    "UPDATE army SET ready = ready + ? WHERE user_id = ?",
                    (int(ready), int(user_id))
                )
                await call.bot.send_message(user_id, "🔝Ваша готовность армии увеличилось на 1")
                conn.commit()
                # print(F"Commited: ready:{ready}, user_id:{user_id}")
            except Exception as e:
                print(f"[ERROR]:update ready: {e}")
        elif is_ready is False:
            cursor.execute("UPDATE army SET ready = 100 WHERE user_id = ?", (int(user_id),))
            await call.bot.send_message(user_id, "🪖Ваша готовность уже состовляет 100!")
            army_ready_state[user_id] = "unblocked"
            ready_army = False
            conn.commit()
        elif is_ready == "error":
            army_ready_state[user_id] = "unblocked"
            ready_army = False
            print("Error in transfer_ready_army")
            
        sleepfor = random.randint(20, 40)
        await asyncio.sleep(sleepfor)

async def start_population_activate(chat_id, user_id):
    global pop_t
    # print(pop_t)
    while pop_t:
        country = await get_country_from_users(user_id)
        params = await get_country_params(country)
        economy = params[2] // 100000
        population_max = (params[3] // 50) + (params[4] // 5) * (params[5] // 40) + economy
        population_min = (params[3] // 100) + (params[4] // 15) * (params[5] // 40) + economy
        if population_max >= 9000:
            population_max = POPULATION_MAX
        if population_min >= 5000:
            population_min = POPULATION_MIN
        population = random.randint(population_min, population_max)
        # print(f"Population Before: {population}")
        population_bonus = params[6]
        population_bonus_amount = population * population_bonus
        population += population_bonus_amount
        # print(f"Popualtion after bonus:{population}")
        
        if population <= 0:
            print(population)
            population = random.randint(1, 2)
            # print("start min popualtion")
        await transfer_population(population, country, True)
        await bot.send_message(chat_id=chat_id, text=f"👩‍🍼 Было рождено {population} людей из страны {country}.")
        
        sleepfor = random.randint(20, 40)
        await asyncio.sleep(sleepfor)
        
async def start_production_activate(chat_id, user_id):

    # Вычисления для максимальных и минимальных доходов
    def calculate_income_params(params):
        economy_max = params[2] // 45
        population_max = params[3] // 30
        happiness_max = params[4] // 24
        income_max = economy_max + population_max * happiness_max

        econome_min = params[2] // 80
        population_min = params[3] // 50
        happiness_min = params[4] // 48
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
        if income_max >= PRODUCTION_MAX:
            income_max = PRODUCTION_MAX
        income = random.randint(income_min, income_max)
        
        await transfer_money(income, user_id, True)
        await bot.send_message(chat_id=chat_id, text=f"💰 Было получено {income} монет из страны {country}.")
        
        sleepfor = random.randint(20, 40)
        await asyncio.sleep(sleepfor)

async def invest_task(country, money, chat_id):
    Invest = True
    numOfInvest = 0
    economy_min = money // 20
    economy_max = money // 10
    economy_bonus_get = await get_country_params(country=country)
    economy_bonus = economy_bonus_get[7]
    while Invest:
        numOfInvest += 1
        economy = random.randint(economy_min, economy_max)
        economy_bonus_amount = economy * economy_bonus
        economy += economy_bonus_amount
        if numOfInvest == 6:
            Invest = False
            break
        try:
            cursor.execute("UPDATE countries SET economy = economy + ? WHERE name = ?", (economy, country))
            await bot.send_message(chat_id=chat_id, text=f"💹 Было получено {economy} единиц экономики вашей страны! 💰")
        except BaseException as e:
            await bot.send_message(chat_id=chat_id, text="🚨 Ошибка: " + str(e))
            Invest = False
            break
        
        sleepfor = random.randint(20, 40)
        await asyncio.sleep(sleepfor)
        
async def start_party_activate(chat_id, user_id, country, money):
    global party_t
    numOfParty = 0
    params = await get_country_params(country)
    happiness_min = math.ceil(money / 2000)
    happiness_max = math.ceil(money / 500)
    happiness_bonus = params[8]
    party_t = True
    await transfer_happiness(30, country, False)

    while party_t:
        current_happiness = await get_country_params(country)

        check = await party_checks(numOfParty, current_happiness, user_id, country)
        numOfParty += 1
        # print(F"Check:{check}, NumOfParty:{numOfParty}")
        if check:
            happiness = random.randint(happiness_min, happiness_max)
            happiness_bonus_amount = happiness * happiness_bonus
            happiness += happiness_bonus_amount
            await bot.send_message(chat_id=chat_id, text=f"📈 Счастье увеличилось на {happiness}! 🎭")
            await transfer_happiness(happiness, country, True)  # 🔄 Обновляем значение в БД
            
            sleepfor = random.randint(3, 5)
            await asyncio.sleep(sleepfor)
        else:
            await bot.send_message(chat_id=chat_id, text="🎉 Праздник закончился!")
            break
    
async def party_checks(numOfParty, current_happiness, user_id, country):
    first_check = False
    second_check = False
    if numOfParty >= 8:
                await bot.send_message(chat_id=user_id, text="🎉 Праздник закончился!")
                party_t = False
                party_state[user_id] = "unblocked"
                return
    else:
        first_check = True
    if current_happiness[4] >= 100:
                await bot.send_message(chat_id=user_id, text="🎊 Счастье достигло 100%! Праздник завершен.")
                party_t = False
                party_state[user_id] = "unblocked"
                await set_happy_max(country)
    else:
        second_check = True
    if first_check and second_check:
        return True
    else:
        return False

# endregion

# region 2 ⁡⁢⁣⁣​‌‍‌InCountryMethods⁡​

@r.callback_query(F.data == "invest")
async def investigate(callback_query: CallbackQuery, state: FSMContext):
    is_user = await chek_is_user(callback_query.from_user.id)
    if is_user is False:
        await callback_query.message.answer("🚫Вы не зарегистрированы")
        return
    
    await callback_query.message.answer("💰 Введите сумму инвестиции на вашу страну:\n🚫Отмена - отмена")
    await state.set_state(Investigate.num)
    
@r.message(Investigate.num)
async def process_investigate(message: Message, state: FSMContext):
    global numOfInvest, Invest
    if message.text.lower() == "отмена":
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
    country_name = await get_country_from_users(user_id=user_id)
    country = await get_country_params(country=country_name)
    happiness = country
    
    if is_user == False:
        await callback_query.answer("❌ Вы не зарегистрированы.")
        party_t = False
        return
    
    if user_id in user_states2 and user_states2[user_id] == "blocked":
        await callback_query.answer("Праздник уже начат. Подождите 7 минут до окончания праздника")
        return
    
    party_state[user_id] = "blocked"
    
    await callback_query.message.answer("💵Введите сумму которую потратите на праздник: ")
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
            await message.reply("😡Ваше население взбушевалось из-за маленького праздника -10 счастья")
            await transfer_happiness(10, country, False)
            return
            
        try:
            await transfer_money(int(message.text), message.from_user.id, False)
            asyncio.create_task(start_party_activate(chat_id, user_id, country, int(message.text)))
            await message.reply("Праздник начато. Вы будете получать отчет о празднике каждые 5 секунд.")
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
    
# region 3​‌‍‌ ⁡⁣⁣⁢earn money and product⁡​

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
    
# region 4 ⁡⁢⁢⁢​‌‌‍‍guest methods⁡​

@r.message(Command("unlogin"))
async def logout_account(message: Message, state: FSMContext):
    global captcha
    
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.answer("🚫Вы не зарегистрированы")
        return
    
    captcha = await generate_captcha()
    await message.answer(f"🪪Введите капчу для подтверждения выхода:\nкод: {captcha}\n🚫Отмена - отмена")
    await state.set_state(Logout.captcha)
    
@r.message(Logout.captcha)
async def check_captcha(message: Message, state: FSMContext):
    global captcha
    if message.text.lower() == captcha.lower():
        user_id = message.from_user.id
        await state.clear()
        await message.answer("↪️Выход из аккаунта успешно завершен.")
        await ban_user(user_id, user_id)
    elif message.text.lower() == "отмена":
        await state.clear()
        await message.answer("↪️Выход отменен.")
    else:
        await message.answer("❗️Неправильный код. Попробуйте еще раз./unlogin")

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
    is_user = await chek_is_user(message.from_user.id)
    if is_user == False:
        await message.answer("🚫Вы не зарегистрированы")
        return
    
    if not message.reply_to_message:
        await message.reply("↪️Вы должны ответить на сообщение пользователя, чтобы передать валюту.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("💵Вы должны указать сумму. Пример: дать 100")
            return
        
        amount = int(parts[1])

        if amount <= 0:
            await message.reply("💵Сумма должна быть положительной.")
            return

    except ValueError:
        await message.reply("💵Некорректная сумма. Пример: дать 100")
        return

    from_user_id = message.from_user.id
    to_user_id = message.reply_to_message.from_user.id


    cursor.execute(F"SELECT money FROM users WHERE user_id = {message.from_user.id}")
    cur = cursor.fetchone()
    money = cur[0]
    if money < amount:
        await message.reply("💵У вас недостаточно средств.")
    
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

# region 5 ⁡⁣⁢⁢​‌‌‍Army⁡​

@r.message(F.text.lower() == 'сражаться')
async def battle(message: Message):
    
    is_user = await chek_is_user(user_id=message.from_user.id)
    if is_user is False:
        await message.answer("🚫Вы не зарегистрированы")
        return
    
    if is_on_cooldown(user_1_id) or is_on_cooldown(user_2_id):
        left_1 = get_cooldown_time_left(user_1_id)
        left_2 = get_cooldown_time_left(user_2_id)

        msg = "⏳ Кулдаун боя!\n"
        if left_1 > 0:
            msg += f"🔹 Вам ждать: {left_1} сек.\n"
        if left_2 > 0:
            msg += f"🔸 Сопернику ждать: {left_2} сек."
        await message.answer(msg)
        return
    
    if not message.reply_to_message:
        await message.answer("⚔️ **Сражение возможно только в ответ на сообщение соперника!**")
        return

    user_1_id, user_2_id = message.from_user.id, message.reply_to_message.from_user.id
    if not check_war_status(user_1_id, user_2_id):
        await message.answer("❌ **Вы не находитесь в войне или у вас перемирие!**")
        return

    army_1, army_2 = await get_army(user_1_id), await get_army(user_2_id)
    if not army_1 or not army_2:
        await message.answer("❌ **Не удалось найти армию одного из пользователей.**")
        return

    attacker_id, defender_id = user_1_id, user_2_id
    attacker_army, defender_army = army_1, army_2
    
    country_name_1 = await get_country_from_users(user_1_id)
    country_name_2 = await get_country_from_users(user_2_id)
    country1 = await get_country_params(country_name_1)
    country2 = await get_country_params(country_name_2)
    army_1_bonus_attack = country1[10]
    army_2_bonus_attack = country2[10]
    army_1_bonus_defense = country1[9]
    army_2_bonus_defense = country2[9]

    def calculate_strength(army, is_attacker, attack_bonus_country, defense_bonus_country, luck=True):
        base_strength = army['soldiers'] + army['cars'] * 5 + army['tanks'] * 10
        if army['soldiers'] < (army['cars'] + army['tanks']):
            return None

        tactic_attack_bonus, tactic_defense_penalty = 1.0, 1.0
        if is_attacker and army['tactic'] == 'attack':
            tactic_attack_bonus, tactic_defense_penalty = 1.3, 0.65
        elif not is_attacker and army['tactic'] == 'defend':
            tactic_attack_bonus, tactic_defense_penalty = 0.65, 1.25

        luck_factor = random.uniform(0.9, 1.1) if luck else 1.0

        total_attack_bonus = tactic_attack_bonus * (1 + attack_bonus_country / 100)
        total_defense_bonus = tactic_defense_penalty * (1 + defense_bonus_country / 100)

        attack_strength = base_strength * total_attack_bonus * luck_factor
        defense_strength = base_strength * total_defense_bonus * luck_factor

        return attack_strength, defense_strength

    # Расчёт силы без удачи для вероятности
    attacker_base_attack, _ = calculate_strength(
        attacker_army, True, army_1_bonus_attack, army_1_bonus_defense, luck=False
    )
    _, defender_base_defense = calculate_strength(
        defender_army, False, army_2_bonus_attack, army_2_bonus_defense, luck=False
    )

    win_chance = 50.0  # по умолчанию
    if attacker_base_attack and defender_base_defense:
        win_chance = attacker_base_attack / (attacker_base_attack + defender_base_defense) * 100

    # Расчёт с рандомом
    attacker_attack, attacker_defense = calculate_strength(
        attacker_army, True, army_1_bonus_attack, army_1_bonus_defense
    )
    defender_attack, defender_defense = calculate_strength(
        defender_army, False, army_2_bonus_attack, army_2_bonus_defense
    )

    if attacker_attack is None:
        await message.answer(f"⚠ **{message.from_user.username} проиграл! Недостаточно солдат.** ❌")
        return
    if defender_attack is None:
        await message.answer(f"⚠ **{message.reply_to_message.from_user.username} проиграл! Недостаточно солдат.** ❌")
        return

    winner_name = loser_name = ""
    if attacker_attack > defender_defense:
        winner, loser = attacker_id, defender_id
        winner_name = message.from_user.username or message.from_user.first_name
        loser_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name

        attacker_loss = 0.25
        defender_loss = 0.5
    else:
        winner, loser = defender_id, attacker_id
        winner_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        loser_name = message.from_user.username or message.from_user.first_name

        attacker_loss = 0.4
        defender_loss = 0.2

    # Снижаем армии
    update_army(
        attacker_id,
        int(attacker_army['soldiers'] * (1 - attacker_loss)),
        int(attacker_army['cars'] * (1 - attacker_loss)),
        int(attacker_army['tanks'] * (1 - attacker_loss))
    )
    update_army(
        defender_id,
        int(defender_army['soldiers'] * (1 - defender_loss)),
        int(defender_army['cars'] * (1 - defender_loss)),
        int(defender_army['tanks'] * (1 - defender_loss))
    )

    await bot.send_message(winner, f"🎉 Поздравляем, {winner_name}! Вы одержали победу над {loser_name}!")
    await bot.send_message(loser, f"😢 Вы проиграли битву против {winner_name}. Подготовьтесь лучше в следующий раз!")

    result_message = (
        f"🏆 **Победитель:** {winner_name}!\n"
        f"💥 Сила удара: {attacker_attack:.0f} vs {defender_defense:.0f}\n"
        f"📊 **Вероятность победы атакующего:** {win_chance:.1f}%\n"
        f"☠️ Потери атакующего: -{int(attacker_loss * 100)}%\n"
        f"☠️ Потери защитника: -{int(defender_loss * 100)}%"
    )
    
    await message.answer(result_message)
    set_cooldown(user_1_id)
    set_cooldown(user_2_id)
    
@r.callback_query(F.data == "ad_ready")
async def ad_ready(call: CallbackQuery):
    global ready_army
    user_id = call.from_user.id
    current_ready_army = await get_ready_army_by_user(user_id)
    
    if current_ready_army == None:
        current_ready_army = 0
        
    if current_ready_army >= 100:
        await call.answer("🔝Ваша готовнасть равняется 100.")
        await set_army_ready_by_user(user_id, 100)
        return
        
    if user_id in army_ready_state and army_ready_state[user_id] == "blocked":
        await call.answer("Тренировка уже запущена.")
        return
        
    await call.answer(text="🔝Повышение готовности войск начато!", show_alert=True)
        
    army_ready_state[user_id] = "blocked"
    ready_army = True
    asyncio.create_task(while_transfer_ready_army(user_id, 1, call))
        
@r.callback_query(F.data == "tactics")
async def tactics(call: CallbackQuery):
    tactic_get = await get_army(call.from_user.id)
    
    if tactic_get:
        tactic = tactic_get['tactic']
        if tactic == "defend":
            await call.message.answer(f"↔️Ваша тактика:\n🔄тактика: {tactic}\nБонусы:\n🆙🛡️-Повышается защита на 40%\n〽️🗡️-Понижается атака на 50%")
        if tactic == "attack":
            await call.message.answer(f"⬆Ваша тактика:\n🔄тактика: {tactic}\nБонусы:\n-🆙🗡️Повышается атака на 35%\n-〽️🛡️Понижается защита на 50%")
        await call.message.answer(f"🆕Для изменения тактики есть кнопки снизу", reply_markup=edit_tactic_kb)
    else:
        await call.message.answer("🚫Ошибка: не удалось получить данные о вашей армии.")

@r.callback_query(F.data == "tactics_defend")
async def tactics_defend(call: CallbackQuery):
    user_id = call.from_user.id
    now = time.time()

    # Проверка кулдауна
    last_used = cooldown_storage_defend.get(user_id)
    if last_used and (now - last_used < COOLDOWN_SECONDS):
        remaining = int(COOLDOWN_SECONDS - (now - last_used))
        await call.answer(f"⏳ Подождите {remaining} сек. перед следующим изменением.", show_alert=True)
        return

    # Обновляем время использования
    cooldown_storage_defend[user_id] = now

    defend = await get_tactics_by_user(user_id=user_id)
    
    if defend != "defend":
        defend = "defend"
        await edit_tactic(call.from_user.id, defend)
        await call.message.answer("✏️ Тактика изменена на 'defend'")
    elif defend == "defend":
        await call.message.answer("❗️ У вас уже тактика изменена на 'defend'")
    else:
        await call.message.answer(f"🚫Error: call.from_user.id:{call.from_user.id}, defend:{defend}, cooldown_storage_defend:{cooldown_storage_defend.get(user_id)}, COOLDOWN_SECONDS:{COOLDOWN_SECONDS}")

@r.callback_query(F.data == "tactics_attack")
async def tactics_attack(call: CallbackQuery):
    user_id = call.from_user.id
    now = time.time()

    # Проверка кулдауна
    last_used = cooldown_storage_attack.get(user_id)
    if last_used and (now - last_used < COOLDOWN_SECONDS):
        remaining = int(COOLDOWN_SECONDS - (now - last_used))
        await call.answer(f"⏳ Подождите {remaining} сек. перед следующим изменением.", show_alert=True)
        return

    # Обновляем время использования
    cooldown_storage_attack[user_id] = now

    attack = await get_tactics_by_user(user_id=user_id)
    
    if attack != "attack":
        attack = "attack"
        await edit_tactic(call.from_user.id, attack)
        await call.message.answer("✏️ Тактика изменена на 'attack'")
    elif attack == "attack":
        await call.message.answer("❗️ У вас уже тактика изменена на 'attack'")
    else:
        await call.message.answer(f"🚫Error: call.from_user.id:{call.from_user.id}, attack:{attack}, cooldown_storage_attack:{cooldown_storage_attack.get(user_id)}, COOLDOWN_SECONDS:{COOLDOWN_SECONDS}")

@r.message(F.text.in_({'Армия','армия','Army'}))
async def army(message: Message):
    user_id = message.from_user.id
    is_user = await chek_is_user(user_id)
    if is_user == False:
        await message.answer("🚫Вы не зарегистрированы")
        return
    is_army = await chek_is_army(user_id=user_id)
    country_name = await get_country_from_users(user_id=user_id)
    if is_army is False:
        cursor.execute("INSERT INTO army(user_id, soldiers, cars, tanks) VALUES(?, ?, ?, ?)", (user_id, 10, 2, 1))
        conn.commit()
        await message.answer("Армия создана!🪖")
    else:
        army_params = await get_army(user_id)
        soldiers = army_params['soldiers']
        cars = army_params['cars']
        tanks = army_params['tanks']
        ready = army_params['ready']
        army = await calculate_army_strength(army_params, country_name=country_name)
        need = army['needed_soldiers']
        strength = army['strength']
        attack_bonus = army['attack_bonus']
        defense_bonus = army['defense_bonus']
        if soldiers <= need:
            await message.answer(f"🚫Не хватка Солдат!{soldiers - need}", reply_markup=armmy_kb)
        else:
            await message.answer(f"--Армия--\nСолдаты - {soldiers - need}🪖, стоимость - 100💵\nМашины - {cars}🛻, стоимость - 1000💵\nТанки - {tanks}💥, стоимость - 3000💵\nГотовность - {ready}🔰\n⚔️Бонус в атаке - {attack_bonus}\n🛡️Бонус в защите - {defense_bonus}\nБаллы - {strength}\nДля познания команд отношении введите - /army_peace", reply_markup=armmy_kb)

@r.message(Command("army_peace"))
async def army_peace_help(message: Message):
    await message.answer("Команды для отношении:\nОбьявить войну - надо ответить на сообщение собеседника\nОбьявить перемирие - надо ответить на сообщение собеседника и быть в войне с ним\nсражаться - надо ответить на сообщение быть в состояние войны также быть в нужной тактике и иметь превосходство либо подобрать тактику которую вы будете использовать чтоб победить в сражении", reply_markup=keyboard_army_peace)

@r.callback_query(F.data == 'sol')
async def add_soldiers(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 100, 10)
    if acc == True:
        await add_army_slodiers(callback.from_user.id, 100, 10)
        await bot.send_message(callback.from_user.id, "10 Солдат успешно прибыли в вашу армию!🪖")
    else:
        await callback.message.answer("Не достаточно денег📉")

@r.callback_query(F.data == 'car')
async def add_сars(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 1000, 5)
    if acc == True:
        await add_army_cars(callback.from_user.id, 1000, 5)
        await callback.message.answer("5 Машин успешно прибыли в вашу армию!🪖")
    else:
        await callback.message.answer("Не достаточно денег📉")

@r.callback_query(F.data == 'tan')
async def add_tanks(callback: CallbackQuery):
    acc = await army_accept(callback.from_user.id, 3000, 1)
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
            await message.reply("🚫Вы не зарегистрированы!")
            return
        if is_user2 == False:
            await message.reply("🚫Враг не зарегистрирован!")
            return
        
        if is_war == True:
            await message.reply("🚫Вы уже объявили войну с этим игроком!")
            return

        if is_army1 == False:
            await message.reply("🚫Вы не создали армию!")
            return
        
        if is_army2 == False:
            await message.reply("🚫Враг не создали армию!")
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

# region 6 ⁡⁢⁣⁢​‌‌‍admin⁡​

@r.message(Command("get_admin"))
async def get_admin(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if not is_admin:
        await message.reply("❌ У вас недостаточно прав.")
        return

    cursor.execute("SELECT user_id FROM admins")
    admins = cursor.fetchall()  # Получаем список всех админов

    if not admins:
        await message.reply("❌ В базе данных нет админов.")
        return

    admin_list = []
    for admin in admins:
        admin_id = admin[0]
        cursor.execute("SELECT name FROM users WHERE user_id = ?", (admin_id,))
        admin_name = cursor.fetchone()
        
        if admin_name:
            admin_list.append(f"🆔 {admin_id} | 👤 {admin_name[0]}")
        else:
            admin_list.append(f"🆔 {admin_id} | ❌ Имя не найдено")

    result_text = "\n".join(admin_list)
    await message.reply(f"👑 **Список администраторов:**\n{result_text}")

@r.message(Command("register_admin"))
async def register_admin(message: Message, state: FSMContext):
    await message.reply("🔑Введите пороль для аутентификации: \nОтмена - отмена")
    await state.set_state(RegisterAdmin.password)
    
@r.message(RegisterAdmin.password)
async def register_admin_password(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
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
    if message.text.lower() == "отмена":
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
    await message.answer("/ban 'ID' - бан игрока по ID\n/givement <id получателя> <сумма>. - Выдача денег по ID\n/create_country 'name' 'economy' 'population' 'happiness' 'temp_rost' - создание страны с добавление ее пораметров\n/delete_country 'name' - удаление страны по названию\n/get_users - получение всех пользователей с их ID и вообщем все информации\n/get_country - получени всех стран с их параметрамит\n/get_admin - получение всех админов\n/update_country - обновление страны по его параметрам\n", reply_markup=keyboard_admin)
    
@r.message(Command("ban"))
async def ban_user_message(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался забанить игрока")
        return
    args = message.text.split()
    if len(args)!= 2:
        if message.reply_to_message:
            ban_user_id = message.reply_to_message.from_user.id
            await ban_user(ban_user_id, message.from_user.id)
            await message.answer(F"❗️Пользователь с ID: {ban_user_id} был забанен", reply_markup=keyboard_admin)
            logging.info(f"Пользователь с ID: {ban_user_id} забанен пользователем с ID: {message.from_user.id}")
            return
        else:
            await message.reply("❗️Неверный формат. Используйте: /ban <id пользователя>")
            logging.info(f"Пользователь с ID: {message.from_user.id} попытался забанить игрока")
            return
    user_id = int(args[1])
    if user_id == admin:
        logging.info(F"Пользователь с ID: {message.from_user.id} пытался забанить разработчика!")
        return
    await ban_user(user_id, message.from_user.id)
    await message.reply(F"❗️Пользователь с ID: {user_id} был забанен", reply_markup=keyboard_admin)
    
@r.message(Command('givement'))
async def givement_pol(message: Message):
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        return
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
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        await state.clear()
        return
    broadcast_text = message.text
    
    if broadcast_text.lower() == "отмена":
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
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        return
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
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        return

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
    is_admin = await chek_is_admin(message.from_user.id)
    if is_admin == False:
        await message.reply("🚨У вас недостаточно прав для выполнения этой операции.")
        logging.info(f"Пользователь с ID: {message.from_user.id} попытался узнать команды админа")
        return
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
        await message.answer("Введите ID админа для удаления🪪:\nОтмена - отмена")
        await state.set_state(Ban.id)
    else:
        await message.reply("У вас не доступа!❌")

    @r.message(Ban.id)
    async def ban_admin_True(message: Message, state: FSMContext):
        if message.text.lower() == "отмена":
            await message.reply("Удаление отменено!")
            await state.clear()
            return
        
        cursor.execute(f"SELECT user_id FROM admins WHERE user_id = {message.text}")
        a = cursor.fetchone()
        adma = a[0]
            
        if adma != None:
            cursor.execute(f"DELETE FROM admins WHERE user_id = {message.text}")
            await bot.send_message(message.text, f"Вы были удалены админом {message.from_user.first_name}")
            await message.reply("Удаление прошло успешно!✅")
            await state.clear()
        else:
            await message.answer("Такого админа нет🙅‍♂️")
    
# endregion