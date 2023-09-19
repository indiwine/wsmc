from django.db.models import TextChoices


class ProfileScreeningStatus(TextChoices):
    PENDING = 'pe', 'В очікуванні'
    WAITING_RUSSIAN = 're', 'Ждун'
    OK = 'ok', 'Норм'
    LDNR = 'ld', 'БОМБАС'
    NATIVE_RUSSIAN = 'nr', 'Росія'
