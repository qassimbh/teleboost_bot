import json
import requests
from flask import Flask, request

app = Flask(__name__)

# تحميل الإعدادات من config.json
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["bot_token"]
ADMIN_ID = config["admin_id"]
API_KEY = config["api_key"]

API_URL = "https://api.kd1s.com/api/v2"

# إرسال رسالة تلغرام
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# تنفيذ طلب من API موقع زيادة
def send_order(link, quantity):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": 13124,
        "link": link,
        "quantity": quantity
    }
    response = requests.post(API_URL, data=payload)
    return response.json()

# حفظ الطلبات
def save_order(link, quantity, user_id):
    order = {
        "user_id": user_id,
        "link": link,
        "quantity": quantity
    }
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(order)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route(f"/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        lines = text.strip().split("\n")
        if len(lines) >= 2:
            link = lines[0]
            quantity = lines[1]
            try:
                quantity = int(quantity)
                result = send_order(link, quantity)
                save_order(link, quantity, chat_id)

                send_message(chat_id, f"✅ تم إرسال الطلب بنجاح.\nرقم الطلب: {result.get('order')}")
                send_message(ADMIN_ID, f"📥 طلب جديد من {chat_id}:\n🔗 {link}\n📦 الكمية: {quantity}")
            except:
                send_message(chat_id, "⚠️ تأكد من أن الكمية رقم صحيح.")
        else:
            send_message(chat_id, "📥 أرسل الرابط في السطر الأول، والكمية في السطر الثاني.")
    return "ok", 200

@app.route("/")
def index():
    return "بوت TeleBoost شغال ✅", 200
