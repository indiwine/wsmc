import logging
from typing import Optional

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db.models import Model, ForeignKey, RESTRICT, CharField, DateField, Index, BooleanField, SET_NULL, JSONField
from tinymce.models import HTMLField

from .smcredential import SmCredential
from .suspectsocialmediaaccount import SuspectSocialMediaAccount
from ..geo.geocoderhelper import GeoCoderHelper
from ..social_media import SocialMediaTypes
from ..social_media.profileauthenticitystatus import ProfileAuthenticityStatus
from ..social_media.profilescreeningstatus import ProfileScreeningStatus

logger = logging.getLogger(__name__)

LOOKUP_COUNTRY_CODES = ['UA']


class SmProfile(Model):
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, editable=False)

    oid = CharField(max_length=512, verbose_name='ID', help_text='ID користувача в соціальній мережі')
    name = CharField(max_length=512, verbose_name="Ім'я", help_text="Ім'я як вказано в соціальній мережі")
    university = CharField(max_length=512, null=True, verbose_name='Освіта')
    location = CharField(max_length=512, null=True, verbose_name='Місце проживання')
    home_town = CharField(max_length=512, null=True, verbose_name='Місце народження')
    birthdate = DateField(null=True, verbose_name="Дата народження",
                          help_text='Може бути вказаний поточний рік у випадку якщо рік не вказан в соц мережі')
    country = CharField(max_length=512, null=True)
    domain = CharField(max_length=512, null=True)
    metadata = JSONField(null=True)

    was_collected = BooleanField(default=False)
    is_reviewed = BooleanField(default=False)
    """
    DEPRECATED
    """

    suspect_social_media = ForeignKey(SuspectSocialMediaAccount, on_delete=SET_NULL, null=True, editable=False)

    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices, verbose_name='Соціальна мережа')

    location_point = PointField(default=None, null=True, blank=True)
    location_known = BooleanField(default=False, editable=False)
    location_precise = BooleanField(default=False, editable=False)

    person_responsible = ForeignKey(User, default=None, null=True, on_delete=SET_NULL, blank=True)

    screening_status = CharField(
        max_length=4,
        choices=ProfileScreeningStatus.choices,
        default=ProfileScreeningStatus.PENDING,
    )

    authenticity_status = CharField(
        max_length=4,
        choices=ProfileAuthenticityStatus.choices,
        default=ProfileAuthenticityStatus.UNKNOWN,
    )

    comment = HTMLField(default='')

    def __str__(self):
        return self.name

    @admin.display(description='ID URL', empty_value='-')
    def id_url(self) -> Optional[str]:
        if self.oid:
            sm = self.credentials.social_media
            if sm == SocialMediaTypes.FB:
                return f'https://www.facebook.com/profile.php?id={self.oid}'

            if sm == SocialMediaTypes.VK:
                return f'https://vk.com/id{self.oid}'

            if sm == SocialMediaTypes.OK:
                return f'https://ok.ru/profile/{self.oid}'

        return None

    @property
    def permalink(self):
        return self.id_url()

    def identify_location(self):
        if self.country != 'Украина':
            return False

        # Already known
        if self.location_known:
            logger.debug('Location already known')
            return True

        # We cannot found location without at least approximate
        if not self.location and not self.home_town:
            logger.warning('Cannot determine location without "location" or "home_town"')
            return False

        has_country = True
        country_request = None
        query_country_codes = None

        if self.country:
            country_request = f'{self.country}, '

        location_query = self.location
        if not location_query:
            location_query = self.home_town

        if country_request:
            location_query = country_request + location_query
        else:
            query_country_codes = LOOKUP_COUNTRY_CODES

        coder = GeoCoderHelper()
        lookup_result = coder.geocode(query=location_query, country_codes=query_country_codes)
        if lookup_result:
            logger.info(f'Profile determent to be {lookup_result}')
            self.location_point = lookup_result.point
            self.location_known = True
            self.location_precise = has_country
            return True

        logger.info(f'Profile location was not found')
        return False

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'
        unique_together = ['oid', 'social_media']
        indexes = [
            Index(fields=[
                'credentials',
                'oid',
                'was_collected',
                'suspect_social_media',
                'social_media',
                'location_known',
                'location_precise',
                'is_reviewed',
                'screening_status',
                'person_responsible',
                'authenticity_status'
            ])
        ]
