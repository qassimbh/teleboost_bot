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

# قائمة الخدمات
services = {
    "13021": "مشاهدات تيك توك رخيصه 😎",
    "13400": "مشاهدات انستا رخيصه 🅰️",
    "14527": "مشاهدات تلي ✅",
    "15007": "لايكات تيك توك جوده عاليه 💎",
    "14676": "لايكات انستا سريعه قويه وجوده عاليه 😎👍"
}

# إرسال رسالة للمستخدم
def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

@app.route("/")
def home():
    return "✅ البوت شغال", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    # معالجة الرسائل النصية
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        lines = text.strip().split("\n")

        if text == "/start":
            keyboard = {
                "inline_keyboard": [
                    [{"text": name, "callback_data": sid}]
                    for sid, name in services.items()
                ]
            }
            send_message(chat_id, "🔘 <b>اختر الخدمة المطلوبة:</b>", reply_markup=keyboard)

        elif chat_id in selected_services and len(lines) >= 2:
            link = lines[0]
            try:
                quantity = int(lines[1])
                service_id = selected_services[chat_id]

                print("🔁 محاولة تنفيذ الطلب...")
                payload = {
                    "key": API_KEY,
                    "action": "add",
                    "service": service_id,
                    "link": link,
                    "quantity": quantity
                }
                print("📤 البيانات المرسلة إلى API:")
                print(payload)

                try:
                    response = requests.post(API_URL, data=payload, timeout=15)
                    print("📥 رد السيرفر:")
                    print(response.text)
                    result = response.json()

                    if "order" in result:
                        order_id = result["order"]
                        send_message(chat_id, f"✅ <b>تم تنفيذ الطلب بنجاح.</b>\n🧾 رقم الطلب: <code>{order_id}</code>")
                        send_message(ADMIN_ID, f"📥 طلب جديد من <code>{chat_id}</code>:\n🔗 <code>{link}</code>\n📦 الكمية: {quantity}\n🔢 الخدمة: {services[service_id]}")
                    else:
                        send_message(chat_id, f"❌ فشل تنفيذ الطلب:\n{result.get('error', 'خطأ غير معروف')}")
                        print(f"⚠️ رد API غير متوقع: {result}")

                except Exception as e:
                    print(f"❌ لم يتم تنفيذ الطلب بسبب خطأ في الاتصال: {e}")
                    send_message(chat_id, "❌ لم نتمكن من الاتصال بالسيرفر. حاول لاحقاً.")

            except Exception as e:
                print(f"❌ خطأ أثناء تنفيذ الطلب: {e}")
                send_message(chat_id, "❌ حدث خطأ أثناء تنفيذ الطلب. يرجى المحاولة لاحقًا.")
                send_message(ADMIN_ID, f"⚠️ خطأ تقني:\n<code>{e}</code>")

        else:
            send_message(chat_id, "📥 أرسل الرابط في السطر الأول والكمية في السطر الثاني بعد اختيار الخدمة.")

    # معالجة الضغط على أزرار الخدمات
    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        service_id = query["data"]

        selected_services[chat_id] = service_id
        send_message(chat_id, f"✅ تم اختيار الخدمة:\n<b>{services[service_id]}</b>\n\n📥 أرسل الرابط في السطر الأول، والكمية في السطر الثاني.")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)s
