import os
import json
import asyncio
from flask import Flask, request
import telebot

# إعداد Flask
app = Flask(__name__)

# إعداد التوكن
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN is not set in environment variables!")
bot = telebot.TeleBot(BOT_TOKEN)

# نقطة webhook لتلقي التحديثات
@app.route('/bot_webhook', methods=['POST'])
def bot_webhook():
    try:
        json_update = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_update)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Error in webhook: {e}")
    return "OK", 200

# إعداد webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{request.host}/bot_webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}", 200

# صفحة التحقق
@app.route('/')
def home():
    return "البوت يعمل بنجاح 🚀!", 200

# تشغيل Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
