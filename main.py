from flask import Flask, request
from threading import Thread
import os
import json
import asyncio
from telegram.ext import Application, CommandHandler
import nest_asyncio
from datetime import datetime, timedelta

# إعداد تطبيق Flask
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح 🚀!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# إعداد الحلقات المترابطة
nest_asyncio.apply()

# ملف المستخدمين
USER_LIST_FILE = "users.json"

# نص الإشعار الافتراضي
daily_message = "🚨 الكويز سيبدأ بعد 5 دقائق! https://t.me/STEP_5117"

# تحميل وحفظ المستخدمين
def load_users():
    if os.path.exists(USER_LIST_FILE):
        with open(USER_LIST_FILE, "r") as file:
            return json.load(file)
    return []

def save_users(users):
    with open(USER_LIST_FILE, "w") as file:
        json.dump(users, file)

users = load_users()

# أوامر Telegram
async def start(update, context):
    await update.message.reply_text(
        "مرحبًا! أنا البوت الخاص بك 🎉.\n"
        "استخدم /register للتسجيل و /unregister لإلغاء التسجيل.\n"
        "سأذكرك يوميًا في الساعة 8:25 مساءً إذا كنت مسجلًا."
    )

async def register(update, context):
    user_id = update.effective_user.id
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        await update.message.reply_text("✅ تم تسجيلك بنجاح!")
    else:
        await update.message.reply_text("❗ أنت مسجل بالفعل!")

async def unregister(update, context):
    user_id = update.effective_user.id
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        await update.message.reply_text("❌ تم إلغاء تسجيلك بنجاح.")
    else:
        await update.message.reply_text("❗ أنت غير مسجل.")

async def send_notifications(application):
    while True:
        now = datetime.now()
        target_time = datetime(now.year, now.month, now.day, 20, 25)
        if now > target_time:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        for user_id in users:
            try:
                await application.bot.send_message(chat_id=user_id, text=daily_message)
            except Exception as e:
                print(f"⚠️ خطأ في الإرسال إلى {user_id}: {e}")

async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("unregister", unregister))

    keep_alive()
    asyncio.create_task(send_notifications(application))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
