# backupbot/utils.py
import subprocess
import datetime
import zipfile
import os

def make_backup(db_name, db_user, db_pass, db_host="127.0.0.1", db_port="3306"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sql_file = f"/tmp/backup_{timestamp}.sql"
    zip_file = f"/tmp/backup_{timestamp}.zip"

    cmd = [
        "mysqldump",
        f"-h{db_host}",
        f"-P{db_port}",
        f"-u{db_user}",
        f"-p{db_pass}",
        db_name,
    ]

    with open(sql_file, "w", encoding="utf-8") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    # ZIP کردن فایل
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sql_file, arcname=os.path.basename(sql_file))

    # حذف فایل اصلی SQL
    os.remove(sql_file)

    return zip_file


from telebot import TeleBot
from django.conf import settings

def send_telegram_message(text):
    bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
    admin_id = int(settings.TELEGRAM_ADMIN_ID)

    bot.send_message(admin_id, text)
