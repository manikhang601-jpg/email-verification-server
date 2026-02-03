from flask import Flask, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

# 🔑 Gmail SMTP setup (replace these)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'manikhang601@gmail.com'   # 👈 apna Gmail
app.config['MAIL_PASSWORD'] = 'pbsn yzhr ipfj apov'          # 👈 Gmail App Password

mail = Mail(app)

# ✅ Memory store for verification status
verification_status = {}

@app.route('/send_verification', methods=['POST'])
def send_verification():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email required"}), 400

    verification_status[email] = None  # reset status

    html_content = f"""
    <h2>Email Verification</h2>
    <p>This are team of AHMAD so earn manoey Click below to verify or reject your email:</p>
    <a href="http://127.0.0.1:5000/verify?result=yes&email={email}"
       style="background-color:green;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">YES ✅</a>
    &nbsp;&nbsp;
    <a href="http://127.0.0.1:5000/verify?result=no&email={email}"
       style="background-color:red;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">NO ❌</a>
    """

    msg = Message(
        subject="Email Verification",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email],
        html=html_content
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/verify')
def verify():
    result = request.args.get('result')
    email = request.args.get('email')

    if not email:
        return "<h2>⚠️ Invalid request.</h2>"

    if result == "yes":
        verification_status[email] = True
        return "<h2>✅ Email verified successfully. You can now return to your app.</h2>"
    elif result == "no":
        verification_status[email] = False
        return "<h2>❌ Verification rejected. This is not your account.</h2>"
    else:
        return "<h2>⚠️ Invalid verification link.</h2>"


@app.route('/check_status', methods=['POST'])
def check_status():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email required"}), 400

    status = verification_status.get(email)
    return jsonify({"status": status}), 200


if __name__ == '__main__':
    app.run(debug=True)
