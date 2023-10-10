import logging
from typing import Optional

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db.models import Model, URLField, BooleanField, CharField

from .smcredential import SmCredential
from ..exceptions import UnknownSocialMediaType
from ..social_media import SocialMediaTypes


logger = logging.getLogger(__name__)

def validate_social_media_url(url: str):
    try:
        SocialMediaTypes.from_url(url)
    except UnknownSocialMediaType:
        raise ValidationError(f'Unknown social media type for {url}')


class SuspectGroup(Model):
    _credential_used: Optional[SmCredential] = None
    url = URLField(unique=True, validators=[validate_social_media_url])
    has_been_collected = BooleanField(default=False)
    sm_type = CharField(max_length=4, choices=SocialMediaTypes.choices, verbose_name='Соціальна мережа', default=None)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.sm_type = SocialMediaTypes.from_url(self.url)
        return super().save(force_insert, force_update, using, update_fields)

    @property
    def credentials(self) -> SmCredential:
        if not self._credential_used:
            self._credential_used = SmCredential.objects.get_next_credential(self.sm_type)

        return self._credential_used

    @sync_to_async
    def afetch_next_credential(self):
        return self.credentials

    def __str__(self):
        return self.url
