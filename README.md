# 🤖 Telegram Followers Bot

بوت تيليجرام تلقائي لطلب خدمات زيادة المتابعين والمشاهدات من موقع [kd1s.com](https://kd1s.com)، يعمل عبر Webhook باستخدام `python-telegram-bot` و `Render`.

## 🚀 المميزات

- إرسال طلبات تلقائيًا إلى موقع kd1s باستخدام API
- لوحة تحكم إدارية مخصصة للمشرف
- دعم الحظر وفك الحظر
- إرسال رسالة ترحيب للمستخدمين
- نظام حفظ الطلبات

## ⚙️ الإعداد

1. أنشئ ملف `config.json` يحتوي على:

```json
{
  "BOT_TOKEN": "6663550850:AAG7srmdEyyz-YOpAcRA1aSqMNGwd-2GOP4",
  "ADMIN_ID": 5581457665,
  "API_KEY": "5be3e6f7ef37395377151dba9cdbd552",
  "API_URL": "https://kd1s.com/api/v2"
}
