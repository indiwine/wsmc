from django.db.models import Model, ForeignKey, RESTRICT, CASCADE, CharField, DateField

from .smcredential import SmCredential
from .suspect import Suspect


class SmProfile(Model):
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    name = CharField(max_length=512)
    university = CharField(max_length=512, null=True)
    location = CharField(max_length=512, null=True)
    birthdate = DateField(null=True)

    def __str__(self):
        return f'{self.suspect.__str__()} у {self.credentials.get_social_media_display()}'

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'
