import os
import json
from flask import Flask, request
import telebot

# إعداد Flask
app = Flask(__name__)

# إعداد التوكن
BOT_TOKEN = os.getenv("BOT_TOKEN")  # جلب التوكن من متغيرات البيئة
if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN is not set in environment variables!")
bot = telebot.TeleBot(BOT_TOKEN)

# ملف لتخزين المستخدمين
USER_LIST_FILE = "users.json"

# النص الافتراضي للإشعارات
daily_message = "🚨 الكويز سيبدأ بعد 5 دقائق!   https://t.me/STEP_5117"

# تحميل قائمة المستخدمين
def load_users():
    if os.path.exists(USER_LIST_FILE):
        try:
            with open(USER_LIST_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("⚠️ ملف users.json تالف. سيتم إعادة إنشائه.")
            return []
    return []

# حفظ قائمة المستخدمين
def save_users(users):
    with open(USER_LIST_FILE, "w") as file:
        json.dump(users, file, indent=4)

# قائمة المستخدمين المسجلين
users = load_users()

# صفحة التحقق الرئيسية
@app.route('/')
def home():
    return "البوت يعمل بنجاح 🚀!", 200

# نقطة webhook لتلقي التحديثات
@app.route('/bot_webhook', methods=['POST'])
def bot_webhook():
    try:
        json_update = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_update)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"⚠️ خطأ في webhook: {e}")
    return "OK", 200

# إعداد webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{request.host}/bot_webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"✅ Webhook set to {webhook_url}", 200

# أوامر Telegram
@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "مرحبًا! استخدم /register للتسجيل و /unregister لإلغاء التسجيل."
    )

@bot.message_handler(commands=["register"])
def register_command(message):
    user_id = message.chat.id
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        bot.send_message(user_id, "✅ تم تسجيلك بنجاح!")
    else:
        bot.send_message(user_id, "❗ أنت مسجل بالفعل!")

@bot.message_handler(commands=["unregister"])
def unregister_command(message):
    user_id = message.chat.id
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        bot.send_message(user_id, "❌ تم إلغاء تسجيلك بنجاح.")
    else:
        bot.send_message(user_id, "❗ أنت غير مسجل.")
