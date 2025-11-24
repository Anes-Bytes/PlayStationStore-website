# backupbot/apps.py
from django.apps import AppConfig
import threading
import os

class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backup'
