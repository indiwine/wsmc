from django.db.models import Model, CharField, PositiveIntegerField


class Suspect(Model):
    name = CharField(max_length=255)
    score = PositiveIntegerField(default=0, verbose_name='Підозрілість')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Підозрюваний'
        verbose_name_plural = 'Підозрювані'
