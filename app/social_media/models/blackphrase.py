from django.db.models import Model, CharField


class BlackPhrase(Model):
    phrase = CharField(max_length=1024, verbose_name='Фраза', help_text="Слово або фраза для пошуку")

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = 'Фраза'
        verbose_name_plural = 'Фрази'
