import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "database/app.db"

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    ''')

    # ✅ Create admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()

    if not admin_user:
        hashed_password = generate_password_hash("admin@123")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hashed_password, "admin"))
        print("✅ Admin user created: admin / admin@123")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
