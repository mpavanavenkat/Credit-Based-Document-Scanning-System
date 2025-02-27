from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt, JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
from flask_cors import CORS
import sqlite3
import os
import difflib
from datetime import datetime, date
import threading
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)


app.config["JWT_SECRET_KEY"] = "supersecretkey"

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

DATABASE_PATH = os.path.abspath("database/app.db")

# ✅ Ensure database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Initialize Database & Create Tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Ensure Users Table Exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        credits INTEGER DEFAULT 20
    )
    ''')

    # ✅ Ensure Documents Table Exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # ✅ Ensure Credit Requests Table Exists (THIS IS NEW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        requested_credits INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # ✅ New: Ensure Scan Logs Table Exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scan_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        scan_date TEXT NOT NULL,
        scan_count INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id),
        UNIQUE(user_id, scan_date) ON CONFLICT REPLACE
    )
    ''')

    # ✅ Ensure Users Table Exists with last_reset column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        credits INTEGER DEFAULT 20,
        last_reset TEXT DEFAULT NULL  -- New column to track last reset date
    )
    ''')



    # ✅ Ensure Admin Exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()

    if not admin_user:
        admin_password = bcrypt.generate_password_hash("admin@123").decode("utf-8")
        cursor.execute("INSERT INTO users (username, password, role, credits) VALUES (?, ?, ?, ?)",
                       ("admin", admin_password, "admin", 999))
        print("✅ Admin user created: admin / admin@123")

    conn.commit()
    conn.close()

# Call this function when the app starts to initialize the database
init_db()


# ✅ User Registration
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

# ✅ User Login
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user["password"], password):
        access_token = create_access_token(identity=str(user["id"]), additional_claims={"role": user["role"]})
        return jsonify({"token": access_token, "role": user["role"]}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# ✅ Fetch User Profile
# ✅ Fetch User Profile with Pending Requests
@app.route("/user/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role, credits, total_requests FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "credits": user["credits"],
            "total_requests": user["total_requests"]
        }
    }), 200

# ✅ Upload & Scan Document (Deducts 1 Credit)
from datetime import datetime
import difflib

@app.route("/scan", methods=["POST"])
@jwt_required()
def scan_document():
    try:
        user_id = get_jwt_identity()

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filename = file.filename.strip()

        if filename == "" or not filename.endswith(".txt"):
            return jsonify({"error": "Only .txt files allowed"}), 400

        # ✅ Normalize the text (lowercase, strip, remove extra spaces)
        content = file.read().decode("utf-8").strip().lower()
        content = " ".join(content.split())

        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Deduct 1 credit per scan
        cursor.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user or user["credits"] <= 0:
            conn.close()
            return jsonify({"error": "Insufficient credits"}), 403

        cursor.execute("UPDATE users SET credits = credits - 1 WHERE id = ?", (user_id,))
        conn.commit()

        # ✅ Store the new document
        cursor.execute("INSERT INTO documents (user_id, filename, content) VALUES (?, ?, ?)", 
                       (user_id, filename, content))
        conn.commit()

        # ✅ Log scan activity
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO scan_logs (user_id, scan_date, scan_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, scan_date) 
            DO UPDATE SET scan_count = scan_count + 1;
        ''', (user_id, today))
        conn.commit()

        # ✅ Fetch only user's own stored documents
        cursor.execute("SELECT filename, content FROM documents WHERE user_id = ?", (user_id,))
        stored_docs = cursor.fetchall()

        matches = []
        for doc in stored_docs:
            doc_content = doc["content"].strip().lower()
            doc_content = " ".join(doc_content.split())  # ✅ Normalize stored text

            similarity = difflib.SequenceMatcher(None, content, doc_content).ratio() * 100
            if similarity > 30:  # ✅ Lowered threshold to catch more matches
                matches.append({"filename": doc["filename"], "similarity": round(similarity, 2)})

        conn.close()

        return jsonify({
            "message": "Document scanned and stored successfully",
            "similar_documents": matches if matches else []
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/scans_per_user", methods=["GET"])
@jwt_required()
def get_scans_per_user():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT users.username, scan_logs.scan_date, scan_logs.scan_count
        FROM scan_logs
        JOIN users ON scan_logs.user_id = users.id
        ORDER BY scan_logs.scan_date DESC
    ''')
    
    scan_data = cursor.fetchall()
    conn.close()

    results = []
    for row in scan_data:
        results.append({
            "username": row["username"],
            "scan_date": row["scan_date"],
            "scan_count": row["scan_count"]
        })

    return jsonify({"scans": results}), 200


# ✅ Fetch User's Past Documents
@app.route("/user/documents", methods=["GET"])
@jwt_required()
def get_user_documents():
    try:
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM documents WHERE user_id = ?", (user_id,))
        documents = cursor.fetchall()
        conn.close()

        if not documents:
            return jsonify({"documents": []})

        return jsonify({
            "documents": [{"filename": doc["filename"]} for doc in documents]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Admin Profile
@app.route("/admin/profile", methods=["GET"])
@jwt_required()
def admin_profile():
    try:
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized access"}), 403

        user_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE id = ? AND role = 'admin'", (user_id,))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            return jsonify({"admin": {"id": admin["id"], "username": admin["username"]}})
        else:
            return jsonify({"error": "Admin profile not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ User Requests Additional Credits
@app.route("/user/request_credits", methods=["POST"])
@jwt_required()
def request_credits():
    user_id = get_jwt_identity()
    data = request.get_json()
    requested_credits = data.get("credits")

    if not requested_credits or requested_credits <= 0:
        return jsonify({"error": "Invalid credit request"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO credit_requests (user_id, requested_credits, status) VALUES (?, ?, 'pending')",
                   (user_id, requested_credits))
    cursor.execute("UPDATE users SET total_requests = total_requests + 1 WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Credit request submitted successfully"}), 201



# ✅ Admin Approves/Deny Credit Request
@app.route("/admin/approve_credit/<int:request_id>", methods=["POST"])
@jwt_required()
def approve_credit(request_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, requested_credits FROM credit_requests WHERE id = ? AND status = 'pending'", (request_id,))
    request_data = cursor.fetchone()
    
    if not request_data:
        return jsonify({"error": "Request not found"}), 404

    user_id, requested_credits = request_data["user_id"], request_data["requested_credits"]

    cursor.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (requested_credits, user_id))
    cursor.execute("UPDATE credit_requests SET status = 'approved' WHERE id = ?", (request_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Credits approved successfully"}), 200

# ✅ Admin Denies Credit Request
@app.route("/admin/deny_credit/<int:request_id>", methods=["POST"])
@jwt_required()
def deny_credit(request_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE credit_requests SET status = 'denied' WHERE id = ?", (request_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Credit request denied"}), 200



# ✅ Fetch Pending Credit Requests (For Admin)
@app.route("/admin/credit_requests", methods=["GET"])
@jwt_required()
def get_credit_requests():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cr.id, u.username, cr.requested_credits FROM credit_requests cr JOIN users u ON cr.user_id = u.id WHERE cr.status = 'pending'")
    requests = cursor.fetchall()
    conn.close()

    return jsonify({"requests": [{"id": r["id"], "username": r["username"], "credits": r["requested_credits"]} for r in requests]}), 200

# ✅ Fetch User's Credit Request Status
@app.route("/user/credit_status", methods=["GET"])
@jwt_required()
def credit_status():
    try:
        user_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch latest pending or last processed request
        cursor.execute("SELECT requested_credits, status FROM credit_requests WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        request_data = cursor.fetchone()
        conn.close()

        # ✅ If no requests exist, return default response
        if not request_data:
            return jsonify({"requested_credits": 0, "status": "No Requests"}), 200

        return jsonify({
            "requested_credits": request_data["requested_credits"],
            "status": request_data["status"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/pending_requests", methods=["GET"])
@jwt_required()
def get_pending_requests():
    try:
        user_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT requested_credits, status FROM credit_requests WHERE user_id = ? AND status = 'pending'", (user_id,))
        requests = cursor.fetchall()
        conn.close()

        return jsonify({"requests": [{"credits": req["requested_credits"], "status": req["status"]} for req in requests]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Identify Most Common Scanned Document Topics
@app.route("/admin/common_topics", methods=["GET"])
@jwt_required()
def get_common_topics():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch all document content
    cursor.execute("SELECT content FROM documents")
    documents = cursor.fetchall()
    conn.close()

    if not documents:
        return jsonify({"topics": []}), 200

    # ✅ Combine all text and split into words
    from collections import Counter
    import re

    all_text = " ".join([doc["content"] for doc in documents])
    words = re.findall(r'\b\w{4,}\b', all_text.lower())  # Ignore small words (less than 4 letters)

    # ✅ Count word occurrences and get top 10 common words
    word_counts = Counter(words).most_common(10)
    topics = [word for word, _ in word_counts]

    return jsonify({"topics": topics}), 200

@app.route("/admin/top_users", methods=["GET"])
@jwt_required()
def get_top_users():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch top users by scan count and credit usage
    cursor.execute('''
        SELECT u.username, 
               u.credits, 
               IFNULL(SUM(sl.scan_count), 0) AS total_scans
        FROM users u
        LEFT JOIN scan_logs sl ON u.id = sl.user_id
        GROUP BY u.id
        ORDER BY total_scans DESC, u.credits DESC
        LIMIT 10
    ''')
    
    users = cursor.fetchall()
    conn.close()

    results = [{"username": row["username"], "credits": row["credits"], "total_scans": row["total_scans"]} for row in users]

    return jsonify({"top_users": results}), 200

# ✅ Fetch Credit Usage Statistics for Admins
@app.route("/admin/credit_usage_stats", methods=["GET"])
@jwt_required()
def get_credit_usage_stats():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch total credits requested, approved, and denied
    cursor.execute('''
        SELECT 
            (SELECT SUM(requested_credits) FROM credit_requests WHERE status = 'pending') AS pending,
            (SELECT SUM(requested_credits) FROM credit_requests WHERE status = 'approved') AS approved,
            (SELECT SUM(requested_credits) FROM credit_requests WHERE status = 'denied') AS denied
    ''')
    
    credit_data = cursor.fetchone()
    conn.close()

    # ✅ Prepare response
    return jsonify({
        "pending": credit_data["pending"] or 0,
        "approved": credit_data["approved"] or 0,
        "denied": credit_data["denied"] or 0
    }), 200

def reset_credits():
    while True:
        now = datetime.now()

        # ✅ Check if it's midnight
        if now.hour == 0 and now.minute == 0:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                today_date = date.today().strftime("%Y-%m-%d")

                # ✅ Reset credits only if they haven't been reset today
                cursor.execute('''
                    UPDATE users 
                    SET credits = 20, last_reset = ?
                    WHERE last_reset IS NULL OR last_reset != ?
                ''', (today_date, today_date))

                conn.commit()
                conn.close()
                print("✅ Credits reset to 20 for all users at midnight.")

            except Exception as e:
                print(f"❌ Error resetting credits: {e}")

        # ✅ Sleep for 60 seconds before checking again
        time.sleep(60)

# ✅ Start the reset task in a background thread
reset_thread = threading.Thread(target=reset_credits, daemon=True)
reset_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=5000)