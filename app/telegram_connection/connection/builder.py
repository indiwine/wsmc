from django.conf import settings
from telegram.client import Telegram


def build_client(phone: str) -> Telegram:
    return Telegram(
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        phone=phone,
        database_encryption_key=settings.TELEGRAM_DATABASE_ENCRYPTION_KEY,
        device_model='WSMC App',
        system_version='latest'
    )
