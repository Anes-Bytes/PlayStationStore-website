from django.core.management.base import BaseCommand
from backup.bot import run_bot

class Command(BaseCommand):
    help = "Run Telegram Bot"

    def handle(self, *args, **kwargs):
        self.stdout.write("Bot is running...")
        run_bot()
