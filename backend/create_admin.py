import sqlite3
from flask_bcrypt import Bcrypt

DATABASE_PATH = "database/app.db"
bcrypt = Bcrypt()

def create_admin():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()

    if not admin_user:
        hashed_password = bcrypt.generate_password_hash("admin@123").decode("utf-8")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hashed_password, "admin"))
        conn.commit()
        print("✅ Admin user created successfully: admin / admin@123")
    else:
        print("✅ Admin user already exists.")

    conn.close()

if __name__ == "__main__":
    create_admin()
