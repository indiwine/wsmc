from django.db.models import Model, CharField, PositiveIntegerField, EmailField
from phonenumber_field.modelfields import PhoneNumberField


class Suspect(Model):
    name = CharField(max_length=255, verbose_name='ФІО', null=True, default=None, blank=True)
    score = PositiveIntegerField(default=0, verbose_name='Підозрілість')
    phone = PhoneNumberField(null=True, default=None, verbose_name='Телефон', blank=True)
    email = EmailField(null=True, default=None, blank=True)

    @property
    def has_name(self):
        return isinstance(self.name, str) and len(self.name) > 0

    def __str__(self):
        if self.has_name:
            return self.name
        return f'Невідома людина #{self.pk}'

    class Meta:
        verbose_name = 'Людина'
        verbose_name_plural = 'Люди'
