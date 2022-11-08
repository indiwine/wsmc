from django.db.models import Model, CharField, BooleanField, ManyToManyField
from phonenumber_field.modelfields import PhoneNumberField

from .telegrambot import TelegramBot


class TelegramAccount(Model):
    phone = PhoneNumberField(unique=True,
                             verbose_name='Телефон')
    name = CharField(max_length=255,
                     null=True,
                     verbose_name="Ім'я",
                     help_text="Ім'я (як записано в Telegram)")
    logged_in = BooleanField(default=False, verbose_name='Логін?')
    bots_to_use = ManyToManyField(TelegramBot,
                                  verbose_name='Бот',
                                  help_text='Боти що можуть бути використані з цим аккаунтом.')

    class Meta:
        verbose_name = 'Обліковий запис Telegram'
        verbose_name_plural = 'Облікові записи Telegram'

    def __str__(self):
        return self.phone.as_international
