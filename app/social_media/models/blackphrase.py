from django.db.models import Model, fields


class BlackPhrase(Model):
    phrase = fields.CharField(max_length=512, verbose_name='Фраза', help_text="Слово або фраза для пошуку")
    wight = fields.PositiveIntegerField(verbose_name='Вага',
                                        help_text='Чим більша вага, тим більш "підозрілою" є ця фраза')

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = 'Фраза'
        verbose_name_plural = 'Фрази'
