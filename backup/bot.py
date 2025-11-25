# bot.py
import threading
import time
import os
import psutil
import subprocess
import pytz
import datetime
from telebot import TeleBot, types
from django.conf import settings
from backup.utils import make_backup
from django.utils import timezone


from core.models import CustomUser, OTP
from products.models import Product
from orders.models import Order
from cart.models import Cart


bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
ADMIN_ID = int(settings.TELEGRAM_ADMIN_ID)
BACKUP_DIR = getattr(settings, "BACKUP_DIR", "/tmp")


def send_to_admin(text):
    try:
        bot.send_message(ADMIN_ID, text)
    except Exception as e:

        print("send_to_admin error:", e)



def get_system_info():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
    except Exception:
        cpu = -1
        ram = -1

    try:
        ping_result = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ping_status = f"✔ Online {ping_result }" if ping_result.returncode == 0 else "❌ Offline"
    except Exception:
        ping_status = "❌ Ping failed"

    try:
        tz = pytz.timezone("Asia/Yerevan")
        server_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        server_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    return {"cpu": cpu, "ram": ram, "ping": ping_status, "time": server_time}


def get_database_info():
    try:
        total_users = CustomUser.objects.count()
    except Exception:
        total_users = -1
    try:
        total_products = Product.objects.count()
    except Exception:
        total_products = -1
    try:
        total_orders = Order.objects.count()
    except Exception:
        total_orders = -1
    try:
        total_paid_orders = Order.objects.filter(status=Order.Status.Paid).count()
    except Exception:
        total_paid_orders = -1
    try:
        total_carts = Cart.objects.count()
    except Exception:
        total_carts = -1
    try:
        total_otps = OTP.objects.count()
    except Exception:
        total_otps = -1

    return {
        "users": total_users,
        "products": total_products,
        "orders": total_orders,
        "paid_orders": total_paid_orders,
        "carts": total_carts,
        "otps": total_otps,
    }



def clean_old_backups(days=3):
    cutoff = time.time() - days * 86400
    try:
        for fname in os.listdir(BACKUP_DIR):
            if fname.startswith("backup_") and fname.endswith(".zip"):
                path = os.path.join(BACKUP_DIR, fname)
                try:
                    if os.path.getmtime(path) < cutoff:
                        os.remove(path)
                        send_to_admin(f"🧹 بکاپ قدیمی حذف شد: {fname}")
                except Exception as e:
                    print("clean_old_backups error:", e)
    except Exception as e:
        print("clean_old_backups dir error:", e)



def auto_backup_loop():
    while True:
        try:
            db = settings.DATABASES["default"]


            file_path = make_backup(
                db_name=db["NAME"],
                db_user=db["USER"],
                db_pass=db["PASSWORD"],
                db_host=db.db["DB_HOST"],
                db_port=db.db["DB_PORT"],
            )

            # اطلاعات
            db_info = get_database_info()
            sys_info = get_system_info()

            report = (
                "📦 **بکاپ خودکار انجام شد**\n"
                f"🕒 زمان: {sys_info['time']}\n\n"
                "📊 **اطلاعات دیتابیس:**\n"
                f"👤 کاربران: {db_info['users']}\n"
                f"📦 محصولات: {db_info['products']}\n"
                f"🛒 سفارشات: {db_info['orders']}\n"
                f"💳 سفارشات پرداخت‌شده: {db_info['paid_orders']}\n"
                f"🧺 سبدها: {db_info['carts']}\n"
                f"🔢 OTP ها: {db_info['otps']}\n\n"
                "🖥 **وضعیت سرور:**\n"
                f"CPU: {sys_info['cpu']}%\n"
                f"RAM: {sys_info['ram']}%\n"
                f"Ping: {sys_info['ping']}\n"
            )

            # ارسال گزارش به ادمین
            bot.send_message(ADMIN_ID, report)

            # ارسال فایل بکاپ به ادمین
            try:
                with open(file_path, "rb") as f:
                    bot.send_document(ADMIN_ID, f, caption="📦 بکاپ خودکار (هر 1 ساعت)")
            except Exception as e:
                bot.send_message(ADMIN_ID, f"❌ ارسال فایل بکاپ به تلگرام ناموفق بود:\n{e}")

            # هشدارها (مثال thresholds)
            try:
                if sys_info["cpu"] != -1 and sys_info["cpu"] > 90:
                    send_to_admin("⚠ هشدار: مصرف CPU بالاتر از 90% است.")
                if sys_info["ram"] != -1 and sys_info["ram"] > 90:
                    send_to_admin("⚠ هشدار: مصرف RAM بالاتر از 90% است.")
                if sys_info["ping"].startswith("❌"):
                    send_to_admin("⚠ هشدار: پینگ به 8.8.8.8 ناموفق است.")
            except Exception as e:
                print("warning check error:", e)

            # پاکسازی بکاپ‌های قدیمی
            clean_old_backups(days=3)

        except Exception as e:
            # هر خطایی رخ دهد به ادمین اطلاع بده
            try:
                bot.send_message(ADMIN_ID, f"❌ خطا در بکاپ خودکار:\n{e}")
            except Exception:
                print("auto_backup_loop fatal error:", e)

        # خواب 1 ساعت
        time.sleep(3600)


# Start background thread
threading.Thread(target=auto_backup_loop, daemon=True).start()


# -----------------------------
#   هندلرهای بات (دستورات و فوروارد)
# -----------------------------
@bot.message_handler(commands=["start"])
def start(message):
    # فقط ادمین توانایی استفاده از دکمه‌ها را دارد
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "دسترسی ندارید 🚫")

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📦 بکاپ دستی", callback_data="manual_backup")
    btn2 = types.InlineKeyboardButton("ℹ وضعیت", callback_data="status")
    keyboard.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "سلام ادمین 😎\nیکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=keyboard,
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # فقط ادمین
    if call.from_user.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "دسترسی ندارید", show_alert=True)

    if call.data == "manual_backup":
        bot.answer_callback_query(call.id, "درحال تهیه بکاپ…")
        try:
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
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ خطا در تهیه بکاپ دستی:\n{e}")

    elif call.data == "status":
        db_info = get_database_info()
        sys_info = get_system_info()
        msg = (
            "📊 **وضعیت سرور**\n"
            f"🕒 زمان: {sys_info['time']}\n\n"
            f"CPU: {sys_info['cpu']}%\n"
            f"RAM: {sys_info['ram']}%\n"
            f"Ping: {sys_info['ping']}\n\n"
            f"👤 کاربران: {db_info['users']}\n"
            f"📦 محصولات: {db_info['products']}\n"
            f"🛒 سفارشات: {db_info['orders']}\n"
            f"💳 پرداخت‌شده: {db_info['paid_orders']}\n"
            f"🧺 سبدها: {db_info['carts']}\n"
            f"🔢 OTP: {db_info['otps']}\n"
        )
        bot.send_message(call.message.chat.id, msg)


# -----------------------------
#   فوروارد کردن هر متنی که کاربر می‌فرستد به ادمین
#   (اما اگر فرستنده ادمین باشد فوروارد نکن)
# -----------------------------
@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "document", "video", "audio"])
def forward_to_admin(message):
    try:
        if message.from_user.id == ADMIN_ID:
            # اگر ادمین خودش فرستاد، نیازی به فوروارد نیست — ولی پیام تایید بده
            return bot.send_message(message.chat.id, "✅ دریافت شد.")
        # متن یا مدیا را به ادمین فوروارد کن (فوروارد امن و ساده)
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "پیام شما به ادمین فرستاده شد ✅")
    except Exception as e:
        print("forward error:", e)
        bot.send_message(message.chat.id, "❌ خطا در ارسال پیام به ادمین.")


# -----------------------------
#   اجرای بات
# -----------------------------
def run_bot():
    bot.polling(none_stop=True)
