from typing import Optional

from django.db.models import Model, URLField

from .smcredential import SmCredential
from ..social_media import SocialMediaTypes


class SuspectGroup(Model):
    _credential_used: Optional[SmCredential] = None
    url = URLField(unique=True)

    @property
    def credentials(self) -> SmCredential:
        if not self._credential_used:
            self._credential_used = SmCredential.objects.get_next_credential(SocialMediaTypes.from_url(self.url))

        return self._credential_used

    def __str__(self):
        return self.url
