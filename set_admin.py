import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'crypto_tracker.db')

def make_me_admin(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Устанавливаем статус админа для твоего логина
    cursor.execute("UPDATE Users SET is_admin = 1 WHERE id = ?", (id,))
    
    if cursor.rowcount > 0:
        print(f"Успех! Пользователь {id} теперь администратор.")
    else:
        print(f"Ошибка: Пользователь с ID {id} не найден.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    my_id = input("Введи свой ID на сайте: ")
    make_me_admin(my_id)