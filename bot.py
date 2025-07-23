import json
import requests
from flask import Flask, request

app = Flask(__name__)

# تحميل الإعدادات من config.json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    TOKEN = config["bot_token"]
    ADMIN_ID = config["admin_id"]
    API_KEY = config["api_key"]
except Exception as e:
    print(f"❌ خطأ في تحميل config.json: {e}")
    exit(1)

API_URL = "https://api.kd1s.com/api/v2"

# إرسال رسالة لتليجرام
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ فشل في إرسال الرسالة: {e}")

# تنفيذ الطلب عبر API
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

# حفظ الطلب في ملف data.json
def save_order(link, quantity, user_id):
    order = {"user_id": user_id, "link": link, "quantity": quantity}
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(order)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return "✅ البوت شغال", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "No message", 200

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    lines = text.strip().split("\n")

    if len(lines) >= 2:
        link = lines[0]
        try:
            quantity = int(lines[1])
            result = send_order(link, quantity)

            if "order" in result:
                save_order(link, quantity, chat_id)
                send_message(chat_id, f"✅ تم إرسال الطلب بنجاح.\n🧾 رقم الطلب: {result['order']}")
                send_message(ADMIN_ID, f"📥 طلب جديد من {chat_id}:\n🔗 الرابط: {link}\n📦 الكمية: {quantity}")
            else:
                send_message(chat_id, "❌ فشل تنفيذ الطلب. تحقق من الرابط أو حاول لاحقًا.")
                print(f"⚠️ رد API غير متوقع: {result}")
        except Exception as e:
            print(f"❌ خطأ داخلي أثناء تنفيذ الطلب: {e}")
            send_message(chat_id, "❌ حدث خطأ أثناء تنفيذ الطلب. يرجى المحاولة لاحقًا أو التواصل مع الإدارة.")
    else:
        send_message(chat_id, "📥 أرسل الرابط في السطر الأول والكمية في السطر الثاني.")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
