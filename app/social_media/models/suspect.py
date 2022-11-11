from django.db.models import Model, CharField, PositiveIntegerField, EmailField
from phonenumber_field.modelfields import PhoneNumberField


class Suspect(Model):
    name = CharField(max_length=255, verbose_name='ФІО')
    score = PositiveIntegerField(default=0, verbose_name='Підозрілість')
    phone = PhoneNumberField(null=True, default=None, verbose_name='Телефон', blank=True)
    email = EmailField(null=True, default=None, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Людина'
        verbose_name_plural = 'Люди'
