import json
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# --- الإعدادات ---
TOKEN = "6663550850:AAG7srmdEyyz-YOpAcRA1aSqMNGwd-2GOP4"  # ضع توكن بوتك هنا
ADMIN_ID = 123456789       # معرفك كمدير البوت

API_KEY = "5be3e6f7ef37395377151dba9cdbd552"  #  API لموقع زيادة المتابعين
API_URL = "https://kd1s.com/api/v2"  # رابط API الموقع (مثال)

DATA_FILE = "orders.json"  # ملف لحفظ الطلبات

# --- تخزين البيانات ---
orders = []
banned_users = set()

# --- دوال مساعدة ---

def load_data():
    global orders, banned_users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            orders = data.get("orders", [])
            banned_users = set(data.get("banned_users", []))

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "orders": orders,
            "banned_users": list(banned_users)
        }, f, ensure_ascii=False, indent=2)

# --- خدمات زيادة المتابعين ---
SERVICES = {
    "13124": "متابعين إنستغرام",
    "13799": "متابعين تيك توك",
    "14872": "متابعين تويتر",
}

# --- أوامر وبوت ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "مستخدم"

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📋 إدارة الخدمات", callback_data="manage_services")],
            [InlineKeyboardButton("📝 الطلبات الأخيرة", callback_data="recent_orders")],
            [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="ban_user")],
            [InlineKeyboardButton("🟢 فك الحظر", callback_data="unban_user")],
            [InlineKeyboardButton("📢 رسالة جماعية", callback_data="broadcast")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🔧 أهلاً بك يا مدير {username}!\n👇 هذه لوحة تحكم البوت:",
            reply_markup=reply_markup
        )
    else:
        if user_id in banned_users:
            await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
            return
        await update.message.reply_text(
            f"أهلاً وسهلاً أخي الكريم {username}!\n👋 استخدم /services لاختيار خدمة زيادة المتابعين."
        )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in banned_users:
        await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
        return

    keyboard = []
    for service_id, service_name in SERVICES.items():
        keyboard.append([InlineKeyboardButton(service_name, callback_data=f"service_{service_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الخدمة التي تريد طلبها:", reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id != ADMIN_ID and not query.data.startswith("service_"):
        await query.edit_message_text("❌ هذه الخاصية محصورة للمدير فقط.")
        return

    if query.data == "manage_services":
        text = "📋 خدمات زيادة المتابعين المتوفرة:\n"
        for sid, name in SERVICES.items():
            text += f"- {name} (الكود: {sid})\n"
        await query.edit_message_text(text)

    elif query.data == "recent_orders":
        if not orders:
            await query.edit_message_text("لا توجد طلبات حالياً.")
        else:
            text = "📝 الطلبات الأخيرة:\n"
            for idx, order in enumerate(orders[-10:], 1):
                text += f"{idx}. @{order['username']} - {SERVICES.get(order['service'], order['service'])} - كمية: {order['quantity']}\n"
            await query.edit_message_text(text)

    elif query.data == "ban_user":
        await query.edit_message_text("أرسل معرف المستخدم (ID) الذي تريد حظره:")
        context.user_data['action'] = 'ban_user'

    elif query.data == "unban_user":
        await query.edit_message_text("أرسل معرف المستخدم (ID) الذي تريد رفع الحظر عنه:")
        context.user_data['action'] = 'unban_user'

    elif query.data == "broadcast":
        await query.edit_message_text("أرسل الرسالة الجماعية التي تريد إرسالها لجميع المستخدمين:")
        context.user_data['action'] = 'broadcast'

    elif query.data.startswith("service_"):
        service_id = query.data.split("_", 1)[1]
        await query.edit_message_text(f"لقد اخترت خدمة: {SERVICES.get(service_id, service_id)}\n"
                                      "أرسل الآن الكمية التي تريد طلبها:")
        context.user_data['action'] = 'place_order'
        context.user_data['service'] = service_id

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    action = context.user_data.get('action')

    if action == 'ban_user' and user_id == ADMIN_ID:
        try:
            uid = int(text)
            banned_users.add(uid)
            save_data()
            await update.message.reply_text(f"تم حظر المستخدم بالمعرف: {uid}")
        except:
            await update.message.reply_text("الرجاء إرسال رقم معرف صالح.")
        context.user_data.pop('action', None)

    elif action == 'unban_user' and user_id == ADMIN_ID:
        try:
            uid = int(text)
            banned_users.discard(uid)
            save_data()
            await update.message.reply_text(f"تم رفع الحظر عن المستخدم بالمعرف: {uid}")
        except:
            await update.message.reply_text("الرجاء إرسال رقم معرف صالح.")
        context.user_data.pop('action', None)

    elif action == 'broadcast' and user_id == ADMIN_ID:
        message = text
        count = 0
        for order in orders:
            try:
                await context.bot.send_message(order["user_id"], message)
                count += 1
            except:
                pass
        await update.message.reply_text(f"تم إرسال الرسالة إلى {count} مستخدم.")
        context.user_data.pop('action', None)

    elif action == 'place_order':
        if user_id in banned_users:
            await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
            context.user_data.pop('action', None)
            return

        try:
            quantity = int(text)
            service_id = context.user_data.get('service')
            if service_id:
                # تنفيذ الطلب عبر API الموقع
                params = {
                    "key": API_KEY,
                    "action": "add",
                    "service": service_id,
                    "link": "رابط_الحساب_أو_الصفحة",  # يمكن تعديل لطلب رابط من المستخدم لاحقاً
                    "quantity": quantity,
                }
                response = requests.get(API_URL, params=params)
                data = response.json()

                if data.get("status") == "success":
                    order_id = data.get("order") or "غير متوفر"
                    orders.append({
                        "user_id": user_id,
                        "username": update.effective_user.username or "مستخدم",
                        "service": service_id,
                        "quantity": quantity,
                        "order_id": order_id
                    })
                    save_data()
                    await update.message.reply_text(
                        f"✅ تم تسجيل طلبك بنجاح!\nرقم الطلب: {order_id}\nالخدمة: {SERVICES.get(service_id)}\nالكمية: {quantity}"
                    )
                else:
                    await update.message.reply_text(f"❌ حدث خطأ في تنفيذ الطلب: {data.get('error', 'Unknown error')}")
            else:
                await update.message.reply_text("حدث خطأ. الرجاء المحاولة مرة أخرى.")
        except ValueError:
            await update.message.reply_text("الرجاء إرسال رقم صحيح للكمية.")
        context.user_data.pop('action', None)

    else:
        await update.message.reply_text("يرجى استخدام الأوامر أو الأزرار للبدء.")

def main():
    load_data()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
