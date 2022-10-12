from django.db.models import Model, ForeignKey, RESTRICT, CASCADE, CharField, DateField
from .smcredentials import SmCredentials
from .suspect import Suspect

class SmProfile(Model):
    credentials = ForeignKey(SmCredentials, on_delete=RESTRICT)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    name = CharField(max_length=512)
    university = CharField(max_length=512, null=True)
    location = CharField(max_length=512, null=True)
    birthdate = DateField(null=True)

    def __str__(self):
        return f'{self.name} на {self.credentials.social_media}'
