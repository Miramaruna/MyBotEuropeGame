import sqlite3

# Создаем базу данных и таблицы
def create_database():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT,
            role TEXT DEFAULT 'Мирный житель',
            money INTEGER DEFAULT 0
        )
    ''')

    # Таблица стран
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            name TEXT PRIMARY KEY,
            economy INTEGER,
            population INTEGER,
            happiness INTEGER,
            temp_rost INTEGER DEFAULT 20
        )
    ''')

    # Добавляем тестовые страны
    countries = [
        ("Франция", 100, 1000, 80),
        ("Германия", 120, 1200, 85),
        ("Испания", 90, 900, 75),
        ("Россия", 150, 1500, 70),
        ("Великобритания", 110, 1100, 88)
    ]
    cursor.executemany('INSERT OR IGNORE INTO countries (name, economy, population, happiness) VALUES (?, ?, ?, ?)', countries)

    conn.commit()

create_database()