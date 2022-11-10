from django.db.models import TextChoices


class OsintModules(TextChoices):
    TG_PHONE_BOT = 'tg_phone_bot', 'Телефон у Telegram ботах'
