import os
import random
import telebot
from flask import Flask, request, abort

TOKEN = os.environ["BOT_TOKEN"]
SECRET = os.environ["WEBHOOK_SECRET"]
URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
games = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "أهلاً بك 🎮\nاكتب /game لبدء لعبة خمن الرقم من 1 إلى 50!")

@bot.message_handler(commands=["game"])
def game(message):
    games[message.from_user.id] = {
        "number": random.randint(1, 50),
        "attempts": 0
    }
    bot.reply_to(message, "🎯 اخترت رقماً من 1 إلى 50!\nخمن باستخدام /guess 25")

@bot.message_handler(commands=["guess"])
def guess(message):
    uid = message.from_user.id

    if uid not in games:
        bot.reply_to(message, "ابدأ أولاً باستخدام /game")
        return

    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(message, "اكتب هكذا: /guess 25")
        return

    try:
        number = int(parts[1])
    except ValueError:
        bot.reply_to(message, "أدخل رقماً صحيحاً.")
        return

    if not 1 <= number <= 50:
        bot.reply_to(message, "اختر رقماً بين 1 و50.")
        return

    games[uid]["attempts"] += 1
    answer = games[uid]["number"]

    if number < answer:
        bot.reply_to(message, "⬆️ الرقم أكبر!")
    elif number > answer:
        bot.reply_to(message, "⬇️ الرقم أصغر!")
    else:
        attempts = games[uid]["attempts"]
        del games[uid]
        bot.reply_to(message, f"🎉 صحيح! الرقم {answer}\nمحاولاتك: {attempts}")

@bot.message_handler(commands=["stopgame"])
def stopgame(message):
    games.pop(message.from_user.id, None)
    bot.reply_to(message, "تم إيقاف اللعبة.")

@app.get("/")
def home():
    return "Guess Number Bot is running!", 200


def webhook():@app.post("/telegram")
def webhook():
    try:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
            app.logger.error("Webhook secret mismatch")
            abort(403)

        data = request.get_json(force=True)
        app.logger.info("Telegram update received: %s", data)

        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])

        return "OK", 200

    except Exception:
        app.logger.exception("Webhook processing failed")
        return "ERROR", 500
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        abort(403)

    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return "OK", 200

bot.remove_webhook()
bot.set_webhook(
    url=f"{URL}/telegram",
    secret_token=SECRET
)
