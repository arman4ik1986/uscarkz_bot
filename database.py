import sqlite3

def init_db():
    conn = sqlite3.connect("cars.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        body TEXT,
        min_price REAL,
        max_price REAL,
        city TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_request(user_id, body, min_price, max_price, city):
    conn = sqlite3.connect("cars.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO requests (user_id, body, min_price, max_price, city) VALUES (?, ?, ?, ?, ?)",
                (user_id, body, min_price, max_price, city))
    conn.commit()
    conn.close()
