from telebot import TeleBot, types
from django.conf import settings
from backup.utils import make_backup
import os

bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("📦 بکاپ دستی", callback_data="manual_backup")
    btn2 = types.InlineKeyboardButton("ℹ وضعیت", callback_data="status")

    keyboard.add(btn1)
    keyboard.add(btn2)

    bot.send_message(
        message.chat.id,
        "سلام ادمین 😎\nیکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "manual_backup":
        bot.answer_callback_query(call.id, "درحال تهیه بکاپ…")
        db = settings.DATABASES["default"]

        file_path = make_backup(
            db_name=db["NAME"],
            db_user=db["USER"],
            db_pass=db["PASSWORD"],
            db_host=db.get("HOST", "127.0.0.1"),
            db_port=db.get("PORT", "3306"),
        )

        with open(file_path, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption="📦 بکاپ دستی")

    elif call.data == "status":
        bot.send_message(call.message.chat.id, "سرور آنلاین است ✔")


def run_bot():
    bot.polling()
