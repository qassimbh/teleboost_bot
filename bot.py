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

# ذاكرة مؤقتة لتخزين الخدمة المختارة لكل مستخدم
selected_services = {}

# قائمة الخدمات المتاحة
services = {
    "13021": "مشاهدات تيك توك رخيصه 😎",
    "13400": "مشاهدات انستا رخيصه 🅰️",
    "14527": "مشاهدات تلي ✅",
    "15007": "لايكات تيك توك جوده عاليه 💎",
    "14676": "لايكات انستا سريعه قويه وجوده عاليه 😎👍"
}

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

@app.route("/")
def home():
    return "✅ البوت شغال", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            # عرض قائمة الخدمات كأزرار شفافة
            keyboard = {
                "inline_keyboard": [
                    [{"text": name, "callback_data": sid}]
                    for sid, name in services.items()
                ]
            }
            send_message(chat_id, "🔘 اختر الخدمة المطلوبة:", reply_markup=keyboard)

    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        service_id = query["data"]

        # حفظ الخدمة المختارة
        selected_services[chat_id] = service_id
        send_message(chat_id, "📥 أرسل الرابط في السطر الأول، والكمية في السطر الثاني.")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
