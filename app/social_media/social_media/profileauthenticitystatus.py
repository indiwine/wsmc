from django.db.models import TextChoices


class ProfileAuthenticityStatus(TextChoices):
    HUMAN = 'hn', 'Людина'
    BOT = 'bt', 'Бот'
    UNKNOWN = 'un', 'Невідомо'
