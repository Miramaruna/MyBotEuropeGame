import sqlite3


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
            capital TEXT,
            economy INTEGER,
            population INTEGER,
            happiness INTEGER,
            temp_rost INTEGER DEFAULT 20
        )
    ''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            role TEXT DEFAULT 'Администратор'
        )
    ''')

    # Добавляем тестовые страны
countries = [
    ('Paris', 'Франция', 2900, 68, 69.9, 20.2),
    ('Berlin', 'Германия', 4000, 83, 71.3, 20.1),
    ("Madrid" ,'Испания', 1800, 47, 67.9, 20),
    ("Moskwa", 'Россия', 1700, 144, 55.5, 19.4),
    ("London", 'Великобритания', 3200, 67, 70.1, 20.3)
    ]
cursor.executemany('INSERT OR IGNORE INTO countries (capital, name, economy, population, happiness, temp_rost) VALUES (?, ?, ?, ?, ?, ?)', countries)

conn.commit()