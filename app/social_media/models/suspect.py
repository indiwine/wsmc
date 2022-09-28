from django.db import models

class Suspect(models.Model):
    name = models.fields.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Підозрюваний'
        verbose_name_plural = 'Підозрювані'