from django.db.models import Model, CharField


class TelegramBot(Model):
    name = CharField(max_length=255)
    code = CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боти'

    def __str__(self):
        return self.name
