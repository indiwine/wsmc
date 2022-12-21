from django.db.models import TextChoices


class ConfidentialInformationType(TextChoices):
    PHONE = 'phone', 'Телефон'
    IBAN = 'iban', 'Рахунок IBAN'
    CREDIT_CARD = 'card', 'Банківська картка'
