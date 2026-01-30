from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import sqlite3

app = Flask(__name__)

# ========== EMAIL CONFIG ==========
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ahmadkhang9867@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbsn yzhr ipfj apov'

mail = Mail(app)

# ========== DATABASE ==========
def get_db():
    return sqlite3.connect("users.db")

with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        verified INTEGER
    )
    """)

# ========== SEND EMAIL ==========
@app.route("/send_verification", methods=["POST"])
def send_verification():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    with get_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO users (email, verified) VALUES (?, ?)",
            (email, 0)
        )

    link_yes = f"https://YOUR_RENDER_URL/verify?email={email}&ok=1"

    msg = Message(
        "Verify Your Email",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email],
        html=f"""
        <h3>Email Verification</h3>
        <a href="{link_yes}"
        style="padding:10px;background:green;color:white;text-decoration:none;">
        VERIFY ✅</a>
        """
    )

    mail.send(msg)
    return jsonify({"message": "Email sent"})

# ========== VERIFY ==========
@app.route("/verify")
def verify():
    email = request.args.get("email")
    ok = request.args.get("ok")

    if ok == "1":
        with get_db() as db:
            db.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
        return "✅ Email Verified. You can close this page."

    return "❌ Invalid link"

# ========== CHECK STATUS ==========
@app.route("/check_status", methods=["POST"])
def check_status():
    email = request.json.get("email")

    with get_db() as db:
        cur = db.execute("SELECT verified FROM users WHERE email=?", (email,))
        row = cur.fetchone()

    return jsonify({"verified": bool(row[0]) if row else False})

# ========== RUN ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
