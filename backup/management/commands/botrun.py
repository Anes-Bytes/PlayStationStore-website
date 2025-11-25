from django.core.management.base import BaseCommand
from backup.bot import run_bot
import traceback

class Command(BaseCommand):
    help = "Run Telegram Backup Bot"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Telegram Backup Bot is starting..."))

        try:
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("🛑 Bot stopped manually."))
        except Exception as e:
            self.stdout.write(self.style.ERROR("❌ Bot crashed with exception:"))
            self.stdout.write(self.style.ERROR(str(e)))
            traceback.print_exc()
