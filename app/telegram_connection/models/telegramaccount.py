from django.db.models import Model, CharField, BooleanField
from phonenumber_field.modelfields import PhoneNumberField


class TelegramAccount(Model):
    phone = PhoneNumberField(unique=True)
    name = CharField(max_length=255, null=True)
    logged_in = BooleanField(default=False)

    def __str__(self):
        return self.phone.as_international
