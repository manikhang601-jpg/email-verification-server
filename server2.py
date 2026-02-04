from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import random
import smtplib
import time

# ================= BASIC SETUP =================
app = Flask(__name__)
CORS(app)

DB_NAME = "users.db"

EMAIL_SENDER = "YOUR_GMAIL@gmail.com"
EMAIL_PASSWORD = "YOUR_APP_PASSWORD"   # Gmail App Password
OTP_EXPIRY_SECONDS = 20 * 60  # ✅ 20 minutes

# ================= DATABASE =================
def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            code TEXT,
            verified INTEGER,
            created_at INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= EMAIL SENDER =================
def send_email(to_email, code):
    subject = "Email Verification Code"
    body = f"Your verification code is: {code}\n\nThis code is valid for 20 minutes."
    message = f"Subject: {subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, to_email, message)
    server.quit()

# ================= SEND CODE API =================
@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_db()
    cur = conn.cursor()

    # already verified?
    cur.execute("SELECT verified FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    if row and row[0] == 1:
        conn.close()
        return jsonify({"status": "already_verified"})

    code = str(random.randint(100000, 999999))
    created_at = int(time.time())

    cur.execute("""
        INSERT OR REPLACE INTO users (email, code, verified, created_at)
        VALUES (?, ?, ?, ?)
    """, (email, code, 0, created_at))

    conn.commit()
    conn.close()

    send_email(email, code)

    return jsonify({"status": "code_sent"})

# ================= VERIFY CODE API =================
@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Email and code required"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT code, created_at FROM users WHERE email=?
    """, (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"verified": False, "reason": "not_found"})

    saved_code, created_at = row
    current_time = int(time.time())

    # ⏰ 20 minutes expiry
    if current_time - created_at > OTP_EXPIRY_SECONDS:
        conn.close()
        return jsonify({"verified": False, "reason": "expired"})

    if saved_code == code:
        cur.execute("""
            UPDATE users SET verified=1 WHERE email=?
        """, (email,))
        conn.commit()
        conn.close()
        return jsonify({"verified": True})

    conn.close()
    return jsonify({"verified": False, "reason": "wrong_code"})

# ================= CHECK VERIFIED (OPTIONAL) =================
@app.route("/check", methods=["POST"])
def check_user():
    data = request.get_json()
    email = data.get("email")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT verified FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()

    if row and row[0] == 1:
        return jsonify({"verified": True})

    return jsonify({"verified": False})

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
