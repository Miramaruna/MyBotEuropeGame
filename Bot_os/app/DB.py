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

cursor.execute('''
        CREATE TABLE IF NOT EXISTS army (
            user_id INTEGER PRIMARY KEY,
            soldiers INTEGER DEFAULT 0,
            cars INTEGER DEFAULT 0,
            tanks INTEGER DEFAULT 0
        )
    ''')

cursor.execute('''
        CREATE TABLE IF NOT EXISTS wars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country1 TEXT,
            country2 TEXT,
            result TEXT
        )
    ''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS peace_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL, 
            status TEXT DEFAULT 'pending',
            PRIMARY KEY (sender_id, receiver_id)
        )
    ''')

    # Добавляем тестовые страны
countries = [
    ('Paris', 'Франция', 3100, 68, 69.9, 20.2),
    ('Berlin', 'Германия', 4000, 83, 71.3, 20.1),
    ("Madrid" ,'Испания', 1800, 47, 67.9, 20),
    ("Moskwa", 'Россия', 6320, 144, 55.5, 19.4),
    ("London", 'Великобритания', 3200, 67, 70.1, 20.3),
    ("Rome", 'Италия', 3200, 43, 70.7, 20.1)
    
    ]
cursor.executemany('INSERT OR IGNORE INTO countries (capital, name, economy, population, happiness, temp_rost) VALUES (?, ?, ?, ?, ?, ?)', countries)

conn.commit()