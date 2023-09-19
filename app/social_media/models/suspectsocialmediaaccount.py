from django.db.models import Model, URLField, ForeignKey, RESTRICT, CASCADE

from .smcredential import SmCredential
from .suspect import Suspect


class SuspectSocialMediaAccount(Model):
    link = URLField()
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    def __str__(self):
        return f'{self.suspect.__str__()} у {self.credentials.get_social_media_display()}'

    def fetch_bot_check_link(self) -> str:
        from .smprofile import SmProfile
        try:
            profile = SmProfile.objects.get(credentials=self.credentials, suspect=self.suspect)
            id_url = profile.id_url()
            if id_url:
                return id_url
            return self.link
        except SmProfile.DoesNotExist:
            return self.link

    class Meta:
        unique_together = ['credentials', 'suspect']
        verbose_name = 'Аккаунт підозрюваного'
        verbose_name_plural = 'Аккаунти підозрюваних'
