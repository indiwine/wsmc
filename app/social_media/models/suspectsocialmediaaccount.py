from django.db.models import Model, URLField, ForeignKey, RESTRICT, CASCADE
from .smcredentials import SmCredentials
from .suspect import Suspect

class SuspectSocialMediaAccount(Model):
    link = URLField()
    credentials = ForeignKey(SmCredentials, on_delete=RESTRICT)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    def __str__(self):
        return f'Аккакунт "{self.suspect.name}" у "{self.credentials.__str__()}"'

    class Meta:
        unique_together = ['credentials', 'suspect']
        verbose_name = 'Аккакунт підозрюванорго'
        verbose_name_plural = 'Аккакунти підозрюваних'