import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Токен бота
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния для регистрации
class Registration(StatesGroup):
    name = State()
    country = State()

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Добро пожаловать в игру. Используй /register чтобы зарегистрироваться.")

# Команда /register
@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    await message.reply("Введите ваше имя:")
    await Registration.name.set()

# Обработка имени
@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Отлично! Теперь выберите страну из списка: /countries")
    await Registration.country.set()

# Команда /countries
@dp.message_handler(commands=['countries'], state=Registration.country)
async def choose_country(message: types.Message):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM countries')
    countries = cursor.fetchall()
    conn.close()

    countries_list = "\n".join([country[0] for country in countries])
    await message.reply(f"Доступные страны:\n{countries_list}\n\nВведите название страны:")

# Обработка выбора страны
@dp.message_handler(state=Registration.country)
async def process_country(message: types.Message, state: FSMContext):
    country = message.text
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # Проверяем, есть ли такая страна
    cursor.execute('SELECT name FROM countries WHERE name = ?', (country,))
    if cursor.fetchone():
        # Сохраняем данные пользователя
        user_data = await state.get_data()
        user_id = message.from_user.id
        name = user_data['name']

        cursor.execute('''
            INSERT INTO users (user_id, name, country, role)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, country, 'Президент'))

        conn.commit()
        conn.close()

        await message.reply(f"Вы выбрали {country}! Теперь вы Президент этой страны.")
        await state.finish()
    else:
        await message.reply("Такой страны нет в списке. Попробуйте ещё раз.")

# Команда /info
@dp.message_handler(commands=['info'])
async def show_info(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name, country, role FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        name, country, role = user
        await message.reply(f"Имя: {name}\nСтрана: {country}\nРоль: {role}")
    else:
        await message.reply("Вы не зарегистрированы. Используйте /register.")

# Команда /country_info
@dp.message_handler(commands=['country_info'])
async def show_country_info(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('SELECT country FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        country = user[0]
        cursor.execute('SELECT economy, population, happiness FROM countries WHERE name = ?', (country,))
        country_info = cursor.fetchone()

        if country_info:
            economy, population, happiness = country_info
            await message.reply(f"Информация о стране {country}:\nЭкономика: {economy}\nНаселение: {population}\nСчастье: {happiness}%")
        else:
            await message.reply("Информация о вашей стране отсутствует.")
    else:
        await message.reply("Вы не зарегистрированы. Используйте /register.")

    conn.close()

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)