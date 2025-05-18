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

cursor.execute('''
        CREATE TABLE IF NOT EXISTS battle_cooldowns (
            user_id INTEGER PRIMARY KEY,
            cooldown_until INTEGER
    );
''')

    # Таблица стран

cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            role TEXT DEFAULT 'Администратор'
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
        UNIQUE(sender_id, receiver_id)  -- Гарантирует уникальность пары
    )
''')

cursor.execute('''
        CREATE TABLE IF NOT EXISTS army (
            user_id INTEGER PRIMARY KEY,
            soldiers INTEGER DEFAULT 0,
            cars INTEGER DEFAULT 0,
            tanks INTEGER DEFAULT 0,
            tactic TEXT DEFAULT 'defend',
            ready INTEGER DEFAULT False
        )
    ''')

cursor.execute('''

        CREATE TABLE IF NOT EXISTS countries (
            name TEXT PRIMARY KEY,
            capital TEXT,
            economy INTEGER,
            population INTEGER,
            happiness INTEGER,
            temp_rost INTEGER DEFAULT 20,
            population_bonus INTEGER DEFAULT 0,
            economy_bonus INTEGER DEFAULT 0,
            happiness_bonus INTEGER DEFAULT 0,
            defend_bonus INTEGER DEFAULT 0,
            attack_bonus INTEGER DEFAULT 0
        )
    ''')

    # Добавляем тестовые страны
countries = [
    ('Paris', 'Франция', 3100, 68, 69.9, 20.2, 0.2, 0.4, 0.2, 1.1, 0.2),
    ('Berlin', 'Германия', 4000, 83, 71.3, 20.1, 0.5, 1, 0.3, 0.4, 0.6),
    ('Madrid', 'Испания', 1800, 47, 67.9, 20, 0.2, 0.3, 0.1, 0.4, 0.6),
    ('Moskwa', 'Россия', 6320, 144, 55.5, 19.4, 1.2, 1, 0.2, 0.8, 1.2),
    ('Oslo', 'Норвегия', 2300, 5, 72.5, 20.4, 0.4, 1, 0.4, 0.1, 0.2),
    ('Helsinki', 'Финляндия', 2100, 5, 73.0, 20.2, 0.3, 0.4, 1.9, 0.4, 0.2),
    ('Luxembourg', 'Люксембург', 1800, 0.6, 73.5, 20.3, 0.1, 2, 0.2, 0.1, 0.1),
    ('Warsaw', 'Польша', 2000, 38, 68.8, 20.1, 0.3, 0.4, 0.5, 0.3, 0.2),
    ('London', 'Великобритания', 3200, 67, 70.1, 20.3, 0.4, 0.6, 0.3, 0.5, 0.4),
    ('Rome', 'Италия', 3200, 43, 70.7, 20.1, 0.3, 0.5, 0.4, 0.4, 0.3),
    ('Bucharest', 'Румыния', 1200, 19, 66.8, 19.8, 0.2, 0.3, 0.2, 0.4, 0.3),
    ('Belgrade', 'Сербия', 900, 7, 65.5, 19.5, 0.1, 0.2, 0.3, 0.5, 0.4),
    ('Bern', 'Швейцария', 2500, 8, 74.2, 20.5, 0.5, 1.0, 0.6, 0.3, 0.2),
    ('Brussels', 'Бельгия', 2700, 11, 70.8, 20.2, 0.3, 0.5, 0.3, 0.4, 0.2),
    ('Amsterdam', 'Нидерланды', 2800, 17, 72.1, 20.4, 0.4, 0.6, 0.5, 0.3, 0.2),
    ('Lisbon', 'Португалия', 1500, 10, 68.2, 19.9, 0.2, 0.3, 0.4, 0.3, 0.2),
    ('Dublin', 'Ирландия', 2300, 5, 71.5, 20.3, 0.3, 0.6, 0.5, 0.2, 0.1),
    ('Vienna', 'Австрия', 2600, 9, 71.0, 20.2, 0.4, 0.5, 0.3, 0.3, 0.2),
    ('Copenhagen', 'Дания', 2200, 6, 72.3, 20.4, 0.5, 0.7, 0.6, 0.2, 0.2),
    ('Stockholm', 'Швеция', 2400, 10, 72.0, 20.3, 0.5, 0.6, 0.6, 0.2, 0.3),
    ('Athens', 'Греция', 1700, 10, 67.5, 19.8, 0.2, 0.3, 0.3, 0.4, 0.2),
    ('Sofia', 'Болгария', 1100, 7, 65.8, 19.7, 0.1, 0.2, 0.2, 0.4, 0.3),
    ('Zagreb', 'Хорватия', 1300, 4, 67.2, 19.9, 0.2, 0.3, 0.3, 0.3, 0.2),
    ('Ljubljana', 'Словения', 1400, 2, 68.5, 20.0, 0.3, 0.4, 0.4, 0.3, 0.2),
    ('Bratislava', 'Словакия', 1350, 5, 68.0, 20.0, 0.3, 0.4, 0.4, 0.3, 0.2),
    ('Tallinn', 'Эстония', 1200, 1.3, 69.0, 20.1, 0.3, 0.5, 0.5, 0.2, 0.1),
    ('Riga', 'Латвия', 1150, 1.8, 68.5, 20.0, 0.2, 0.4, 0.4, 0.3, 0.2),
    ('Vilnius', 'Литва', 1180, 2.7, 68.7, 20.0, 0.3, 0.4, 0.5, 0.3, 0.2),
    ('Podgorica', 'Черногория', 900, 0.6, 65.0, 19.6, 0.1, 0.2, 0.3, 0.4, 0.3),
    ('Sarajevo', 'Босния и Герцеговина', 950, 3.2, 65.3, 19.6, 0.2, 0.3, 0.3, 0.4, 0.3),
    ('Skopje', 'Северная Македония', 980, 2.1, 65.8, 19.7, 0.2, 0.3, 0.3, 0.3, 0.2),
    ('Reykjavik', 'Исландия', 1600, 0.4, 74.0, 20.5, 0.5, 1.0, 0.7, 0.2, 0.2),
    ('Valletta', 'Мальта', 1300, 0.5, 70.0, 20.1, 0.2, 0.4, 0.4, 0.2, 0.2),
    ('Prague', 'Чехия', 1700, 10.7, 69.5, 20.2, 0.3, 0.5, 0.5, 0.3, 0.2),
    ('Budapest', 'Венгрия', 1500, 9.6, 67.8, 19.9, 0.2, 0.3, 0.3, 0.3, 0.2)
]

cursor.executemany('INSERT OR IGNORE INTO countries (capital, name, economy, population, happiness, temp_rost, population_bonus, economy_bonus, happiness_bonus, defend_bonus, attack_bonus) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', countries)

conn.commit()