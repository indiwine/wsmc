from django.db.models import Model, DateTimeField, CharField, PositiveIntegerField, ForeignKey, CASCADE

from social_media.models.suspect import Suspect


class ScreeningReport(Model):
    name = CharField(editable=False, max_length=255, verbose_name="Ім'я")
    resulting_score = PositiveIntegerField(default=0, verbose_name='Підозрілість')
    suspect = ForeignKey(Suspect, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Перевірка соцмереж'
        verbose_name_plural = 'Перевірки соцмереж'
