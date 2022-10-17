from django.db.models import Model, URLField, ForeignKey, RESTRICT, CASCADE

from .smcredential import SmCredential
from .suspect import Suspect


class SuspectSocialMediaAccount(Model):
    link = URLField()
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    def __str__(self):
        return f'Аккаунт "{self.suspect.name}" у "{self.credentials.__str__()}"'

    class Meta:
        unique_together = ['credentials', 'suspect']
        verbose_name = 'Аккаунт підозрюваного'
        verbose_name_plural = 'Аккаунти підозрюваних'
