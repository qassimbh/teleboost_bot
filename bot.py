import json
import requests
from flask import Flask, request

app = Flask(__name__)

# تحميل إعدادات البوت من ملف config.json
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

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ فشل في إرسال الرسالة: {e}")

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
            save_order(link, quantity, chat_id)
            send_message(chat_id, f"✅ تم إرسال الطلب بنجاح. رقم الطلب: {result.get('order')}")
            send_message(ADMIN_ID, f"📥 طلب جديد من {chat_id}\n🔗 {link}\n📦 الكمية: {quantity}")
        except Exception as e:
            send_message(chat_id, f"⚠️ حدث خطأ أثناء معالجة الطلب:\n{str(e)}")
            print(f"❌ Error processing order: {e}")
    else:
        send_message(chat_id, "📥 أرسل الرابط في السطر الأول والكمية في السطر الثاني.")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
