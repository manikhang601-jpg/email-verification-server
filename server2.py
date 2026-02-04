from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import os

app = Flask(__name__)

# Email config (Railway variables)
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# Temporary store (simple)
pending_users = {}

@app.route("/")
def home():
    return "Email Verification Server Running ✅"

@app.route("/send_verification", methods=["POST"])
def send_verification():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    token = str(uuid.uuid4())
    pending_users[token] = email

    verify_link = f"https://email-verification-server-production.up.railway.app/verify?token={token}"

    msg = MIMEMultipart()
    msg["From"] = MAIL_USERNAME
    msg["To"] = email
    msg["Subject"] = "Verify your email"

    body = f"""
    Hello 👋

    Click the link below to verify your email:

    {verify_link}

    Thanks ❤️
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return jsonify({"message": "Verification email sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/verify")
def verify():
    token = request.args.get("token")

    if token in pending_users:
        email = pending_users.pop(token)
        return "✅ Email Verified. You can close this page."
    else:
        return "❌ Invalid or expired link"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
