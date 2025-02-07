import sqlite3
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN

from app.handlers import *
from app.keyboards import *
from app.DB import *

if not TOKEN:
    raise ValueError("TOKEN environment variable is not set")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
admin = 5626265763
admin2 = 45

# region start

# Состояния для регистрации
class Registration(StatesGroup):
    name = State()
    country = State()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("👋 Привет! Добро пожаловать в игру. Используй /register, чтобы зарегистрироваться.\n/help - для помощи")

# Команда /register
@dp.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await message.answer("✍ Введите ваше имя:")
    await state.set_state(Registration.name)

# Обработка имени
@dp.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🌍 Отлично! Теперь выберите страну из списка: /countries")
    await state.set_state(Registration.country)

# Команда /countries
@dp.message(Command("countries"))
async def choose_country(message: types.Message):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM countries")
    countries = cursor.fetchall()
    conn.close()

    if countries:
        countries_list = "\n".join([f"🌎 {country[0]}" for country in countries])
        await message.answer(f"📜 Доступные страны:\n{countries_list}\n")
    else:
        await message.answer("⚠ Список стран пуст. Обратитесь к администратору.")

# Обработка выбора страны
@dp.message(Registration.country)
async def process_country(message: types.Message, state: FSMContext):
    country = message.text
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM countries WHERE name = ?", (country,))
    if cursor.fetchone():
        user_data = await state.get_data()
        user_id = message.from_user.id
        name = user_data['name']
        cursor.execute("""
            INSERT INTO users (user_id, name, country, role)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, country, "Президент"))
        conn.commit()
        conn.close()
        await message.answer(f"🎉 Вы выбрали {country}! Теперь вы Президент этой страны! 🏛")
        await state.clear()
    else:
        await message.answer("❌ Такой страны нет в списке. Попробуйте ещё раз.")
        
# endregion

#region info

# Команда /info
@dp.message(Command("info"))
async def show_info(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, country, role FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        name, country, role = user
        await message.answer(f"🆔 Имя: {name}\n🌍 Страна: {country}\n🏅 Роль: {role}")
    else:
        await message.answer("⚠ Вы не зарегистрированы. Используйте /register.")

# Команда /country_info
@dp.message(Command("country_info"))
async def show_country_info(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT country FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        country = user[0]
        cursor.execute("SELECT economy, population, happiness FROM countries WHERE name = ?", (country,))
        country_info = cursor.fetchone()
        conn.close()
        if country_info:
            economy, population, happiness = country_info
            await message.answer(f"🌍 Информация о стране {country}:\n💰 Экономика: {economy}\n👥 Население: {population}\n😊 Счастье: {happiness}%")
        else:
            await message.answer("⚠ Информация о вашей стране отсутствует.")
    else:
        await message.answer("⚠ Вы не зарегистрированы. Используйте /register.")
        conn.close()
        
#endregion

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(r)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚫 Бот остановлен.")