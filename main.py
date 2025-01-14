import os
import json
import asyncio
from telegram.ext import Application, CommandHandler
import nest_asyncio
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta
from flask import Flask, render_template, request
import telebot


# إصلاح مشاكل الحلقات في Replit
nest_asyncio.apply()

# خادم Flask لتفعيل الرابط
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح 🚀!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ملف لتخزين المستخدمين
USER_LIST_FILE = "users.json"

# النص الافتراضي للإشعارات
daily_message = "🚨الكويز سيبدأ بعد 5 دقائق!   https://t.me/STEP_5117"

# تحميل قائمة المستخدمين من ملف JSON
def load_users():
    if os.path.exists(USER_LIST_FILE):
        with open(USER_LIST_FILE, "r") as file:
            return json.load(file)
    return []

# حفظ قائمة المستخدمين إلى ملف JSON
def save_users(users):
    with open(USER_LIST_FILE, "w") as file:
        json.dump(users, file)

# قائمة المستخدمين المسجلين
users = load_users()

# أمر /start
async def start(update, context):
    await update.message.reply_text(
        "مرحبًا! أنا البوت الخاص بك 🎉.\n"
        "استخدم /register للتسجيل و /unregister لإلغاء التسجيل.\n"
        "سأذكرك يوميًا في الساعة 8:25 مساءً إذا كنت مسجلًا."
    )

# أمر /register لتسجيل المستخدم
async def register(update, context):
    user_id = update.effective_user.id
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        await update.message.reply_text("✅ تم تسجيلك بنجاح! سأذكرك يوميًا في الساعة 8:25 مساءً.")
    else:
        await update.message.reply_text("❗ أنت مسجل بالفعل!")

# أمر /unregister لإلغاء تسجيل المستخدم
async def unregister(update, context):
    user_id = update.effective_user.id
    if user_id in users:
        users.remove(user_id)
        save_users(users)
        await update.message.reply_text("❌ تم إلغاء تسجيلك بنجاح.")
    else:
        await update.message.reply_text("❗ أنت غير مسجل.")

# أمر /broadcast لإرسال رسالة جماعية
async def broadcast(update, context):
    admin_id = 1829361616  # استبدل هذا برقم المستخدم الخاص بك
    if update.effective_user.id != admin_id:
        await update.message.reply_text("❌ هذا الأمر مخصص للمسؤول فقط.")
        return

    if not context.args:
        await update.message.reply_text("❌ الرجاء كتابة الرسالة: /broadcast <message>")
        return

    message = " ".join(context.args)
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 رسالة إدارية:\n{message}")
        except Exception as e:
            print(f"⚠️ لم أتمكن من إرسال الرسالة إلى {user_id}: {e}")

    await update.message.reply_text("✅ تم إرسال الرسالة إلى جميع المستخدمين.")

# أمر /set_daily_message لتغيير نص الإشعارات اليومية
async def set_daily_message(update, context):
    global daily_message
    admin_id = 1829361616  # استبدل هذا برقم المستخدم الخاص بك
    if update.effective_user.id != admin_id:
        await update.message.reply_text("❌ هذا الأمر مخصص للمسؤول فقط.")
        return

    if not context.args:
        await update.message.reply_text("❌ الرجاء كتابة الرسالة: /set_daily_message <message>")
        return

    daily_message = " ".join(context.args)
    await update.message.reply_text("✅ تم تحديث نص الإشعارات اليومية.")

# إرسال الإشعارات اليومية
async def send_notifications(application):
    while True:
        now = datetime.now()
        target_time = datetime(now.year, now.month, now.day, 20, 25)  # وقت الإشعار 8:25 مساءً
        if now > target_time:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        for user_id in users:
            try:
                await application.bot.send_message(chat_id=user_id, text=daily_message)
            except Exception as e:
                print(f"⚠️ لم أتمكن من إرسال رسالة إلى المستخدم {user_id}: {e}")

# الوظيفة الرئيسية لتشغيل البوت
async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # جلب التوكن من المتغيرات البيئية
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("unregister", unregister))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("set_daily_message", set_daily_message))

    # تشغيل خادم Flask
    keep_alive()

    # تشغيل إشعارات التذكير
    asyncio.create_task(send_notifications(application))

    # بدء البوت
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

    app.run(debug=True)
