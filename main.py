import os
import json
import asyncio
from flask import Flask, request, send_from_directory
from datetime import datetime, timedelta
import telebot
##GRRRRRRRRRRRR
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

# تحميل قائمة المستخدمين من ملف JSON
def load_users():
    if os.path.exists(USER_LIST_FILE):
        try:
            with open(USER_LIST_FILE, "r") as file:
                users = json.load(file)
                print(f"✅ تم تحميل {len(users)} مستخدم من users.json")
                return users
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تحميل المستخدمين: {e}")
    print("⚠️ ملف users.json غير موجود. سيتم إنشاء ملف جديد.")
    return []

# حفظ قائمة المستخدمين إلى ملف JSON
def save_users(users):
    try:
        with open(USER_LIST_FILE, "w") as file:
            json.dump(users, file, indent=4)
        print("✅ تم حفظ المستخدمين بنجاح في users.json")
    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء حفظ المستخدمين: {e}")

# قائمة المستخدمين المسجلين
users = load_users()

# صفحة التحقق الرئيسية
@app.route('/')
def home():
    return "البوت يعمل بنجاح 🚀!", 200

# معالجة favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
        "مرحبًا! أنا البوت الخاص بك 🎉.\n"
        "استخدم /register للتسجيل و /unregister لإلغاء التسجيل.\n"
        "سأذكرك يوميًا في الساعة 8:25 مساءً إذا كنت مسجلًا."
    )

@bot.message_handler(commands=["register"])
def register_command(message):
    user_id = message.chat.id
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        bot.send_message(user_id, "✅ تم تسجيلك بنجاح! سأذكرك يوميًا في الساعة 8:25 مساءً.")
    else:
        bot.send_message(user_id, "❗ أنت مسجل بالفعل!")

@bot.message_handler(commands=["unregister"])
def unregister_command(message):
    user_id = message.chat.id
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        bot.send_message(user_id, "❌ تم إلغاء تسجيلك بنجاح.")
        print(f"✅ المستخدم {user_id} تم إلغاء تسجيله.")
    else:
        bot.send_message(user_id, "❗ أنت غير مسجل.")
        print(f"⚠️ المستخدم {user_id} حاول إلغاء التسجيل ولكنه غير موجود.")

# إرسال الإشعارات اليومية
async def send_notifications():
    while True:
        now = datetime.now()
        target_time = datetime(now.year, now.month, now.day, 20, 25)  # وقت الإشعار 8:25 مساءً
        if now > target_time:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        for user_id in users:
            try:
                bot.send_message(user_id, daily_message)
            except Exception as e:
                print(f"⚠️ لم أتمكن من إرسال رسالة إلى المستخدم {user_id}: {e}")

# تشغيل Flask
if __name__ == "__main__":
    # إنشاء مجلد static وإضافة favicon.ico إذا لزم الأمر
    static_path = os.path.join(app.root_path, "static")
    if not os.path.exists(static_path):
        os.makedirs(static_path)
    asyncio.create_task(send_notifications())
    app.run(host="0.0.0.0", port=8000)
