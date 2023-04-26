from django.db.models import Model, URLField, CharField, ForeignKey, RESTRICT

from .smcredential import SmCredential


class SuspectGroup(Model):
    name = CharField(max_length=255, null=True, blank=True)
    url = URLField()
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, null=True)

    def __str__(self):
        if not self.name:
            return f'Untitled group at {self.url}'

        return self.name
