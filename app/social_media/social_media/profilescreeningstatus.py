from django.db.models import TextChoices


class ProfileScreeningStatus(TextChoices):
    PENDING = 'pe', 'В очікуванні'
    RUSSIAN = 're', 'Русня'
    OK = 'ok', 'Норм'
