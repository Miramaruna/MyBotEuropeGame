# region imports

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
from app.imports import *
from app.methods import *
from app.states import *

if not TOKEN:
    raise ValueError("🚨 TOKEN environment variable is not set")

# endregion

# region config

# 🤖 Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
admin = 5626265763
admin2 = 45

# endregion

# region start

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("👋 Привет! Добро пожаловать в игру. Используй /register, чтобы зарегистрироваться.\n/help - для помощи", reply_markup=keyboard_start)

@dp.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await message.answer("✍ Введите ваше имя:\n🚫Отмена - отмена")
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        user = await chek_is_user(message.from_user.id)
    except Exception as e:
        logging.info(F"📌 Регистрация пользователя с ID: {message.from_user.id}")
        
    if message.text.startswith("/"):
        await message.answer("❌Недопустимый символ. Используйте только буквы.")
        await state.clear()
        return
    
    if user == False:
        if message.text.lower() == "отмена":
            await state.clear()
            return
        await state.update_data(name=message.text)
        await message.answer("🌍 Отлично! Теперь выберите страну из списка: /countries")
        await state.set_state(Registration.country)
    else:
        user = await get_user_params(message.from_user.id)
        await message.answer(f"✅ Вы уже зарегистрированы как {user[0]}!")
        await state.clear()

@dp.message(Command("countries"))
async def choose_country(message: types.Message):
    cursor.execute("SELECT name FROM countries")
    countries = cursor.fetchall()

    if countries:
        countries_list = "\n".join([f"🌎 {country[0]}" for country in countries])
        await message.answer(f"📜 Доступные страны:\n{countries_list}\n", reply_markup=keyboard_start)
    else:
        await message.answer("⚠ Список стран пуст. Обратитесь к администратору.")

@dp.message(Registration.country)
async def process_country(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return
    country = message.text
    cursor.execute("SELECT name FROM countries WHERE name = ?", (country,))
    if cursor.fetchone():
        user_data = await state.get_data()
        user_id = message.from_user.id
        cursor.execute('SELECT country FROM users WHERE country=?', (country,))
        is_country = cursor.fetchone()
        if is_country is None:
            name = user_data['name']
            cursor.execute("""
                INSERT INTO users (user_id, name, country, role)
                VALUES (?, ?, ?, ?)
            """, (user_id, name, country, "🏛 Президент"))
            conn.commit()
            await message.answer(f"🎉 Вы выбрали {country}! Теперь вы Президент этой страны! 🏛")
        else:
            name = user_data['name']
            cursor.execute("""
                INSERT INTO users (user_id, name, country, role)
                VALUES (?, ?, ?, ?)
            """, (user_id, name, country, "👤 Житель"))
            conn.commit()
            await message.answer(f"🎉 Вы выбрали {country}! Теперь вы Житель этой страны! 👤")
        logging.info(F"✅ Был зарегистрирован новый пользователь с ID:{message.from_user.id}")
        await state.clear()
    else:
        await message.answer("❌ Такой страны нет в списке. Попробуйте ещё раз.")
# endregion

# region info

@dp.message(Command("info"))
async def show_info(message: types.Message):
    user = message.from_user.id
    is_user = await chek_is_user(user)
    if is_user == False:
        await message.reply("⚠ Вы не зарегистрированы. Используйте /register")
        return
    user_params = await get_user_params(user)
    cursor.execute("SELECT * FROM wars WHERE country1 = ? OR country2 = ?", (message.from_user.id, message.from_user.id))
    wars = cursor.fetchone()
    if wars != None:
        country1_name = await get_country_from_users(user)
        country2_name = await get_country_from_users(wars[2])    
    
    if user_params:
        name, country, role, money = user_params
        await message.answer(f"🆔 Имя: {name}\n🌍 Страна: {country}\n🏅 Роль: {role}\n💵 Деньги : {money}", reply_markup=keyboard_start)
    else:
        await message.answer("⚠ Вы не зарегистрированы")
    if wars:
        id, country1, country2, result = wars
        await message.answer(f"⚔️ Сражения:\n️ 🏳️ Страна 1: {country1_name}\n️ 🏳️ Страна 2: {country2_name}\n🏁 Результат: {result}", reply_markup=keyboard_start)
    else:
        await message.answer("⚔️У вас нет ни одного сражения.")
        
@dp.message(Command("country_info"))
async def show_country_info(message: types.Message):
    user_id = message.from_user.id
    is_user = await chek_is_user(user_id)
    if is_user:
        country_name = await get_country_from_users(user_id)
        country = await get_country_params(country=country_name)
        if country:
            name, capital, economy, population, happiness, temp_rost, *rest = country

            # Приводим к float и форматируем до двух знаков после запятой
            economy = f"{float(economy):.2f}"
            population = f"{float(population):.2f}"
            happiness = f"{float(happiness):.2f}"
            temp_rost = f"{float(temp_rost):.2f}"

            await message.answer(
                f"🌍 Информация о стране {name}:\n"
                f"🏛 Столица: {capital}\n"
                f"💰 Экономика: {economy}\n"
                f"👥 Население: {population}\n"
                f"😊 Счастье: {happiness}\n"
                f"📈 Темп роста: {temp_rost}%",
                reply_markup=keyboard_countries_methods
            )
        else:
            await message.answer("⚠ Информация о вашей стране отсутствует.")
    else:
        await message.answer("⚠ Вы не зарегистрированы. Используйте /register.")
        
@dp.message(Command("info_bot"))
async def show_info_bot(message: Message):
    await message.answer("🤖 Информация о боте:\n⚙️ Версия: 1.1.5\n🐍 Язык: Python\n💾 База данных: Sqlite3\n🕹 Разработчик: Miramar\n🔗 Github: https://github.com/Miramaruna/MyBotEuropeGame", reply_markup=keyboard_start)
    
# endregion

# region main
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
# endregion
