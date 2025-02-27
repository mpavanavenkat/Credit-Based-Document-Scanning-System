import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "database/app.db"

def reset_admin_password():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    new_password = "admin@123"
    hashed_password = generate_password_hash(new_password)

    cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (hashed_password,))
    conn.commit()
    conn.close()

    print("✅ Admin password reset successfully to: admin@123")

if __name__ == "__main__":
    reset_admin_password()
