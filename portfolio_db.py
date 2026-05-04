import sqlite3
import os

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'crypto_tracker.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            amount REAL NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    return conn

async def get_user_portfolio(user_id: int) -> dict[str, float]:
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT coin_id, amount FROM Portfolio WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    portfolio = {}
    for row in rows:
        portfolio[row["coin_id"]] = row["amount"]
    return portfolio


# ------------------------------------------------------------
# 2. Добавить или обновить актив
# ------------------------------------------------------------
async def add_or_update_asset(user_id: int, coin_id: str, amount: float):

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, amount FROM Portfolio WHERE user_id = ? AND coin_id = ?",
        (user_id, coin_id)
    )
    existing = cursor.fetchone()
    if existing:
        new_amount = amount
        cursor.execute(
            "UPDATE Portfolio SET amount = ? WHERE id = ?",
            (new_amount, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO Portfolio (coin_id, amount, user_id) VALUES (?, ?, ?)",
            (coin_id, amount, user_id)
        )
    conn.commit()

async def delete_asset(user_id: int, coin_id: str):\

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Portfolio WHERE user_id = ? AND coin_id = ?",
        (user_id, coin_id)
    )
    conn.commit()