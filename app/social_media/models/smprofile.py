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

    # TODO Removal
    # suspect = ForeignKey(Suspect, null=True, on_delete=CASCADE)

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

    comment = HTMLField(default='', blank=True)

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
                if self.metadata and 'permalink' in self.metadata:
                    return self.metadata['permalink']
                return None

        return None

    @property
    def permalink(self):
        return self.id_url()

    @property
    def has_location_or_home_town(self) -> bool:
        return bool(self.location) or bool(self.home_town)

    @property
    def has_country(self) -> bool:
        return bool(self.country)

    def get_geo_query(self) -> str:
        """
        Get query for geocoding in plain text representation
        @return:
        """
        assert self.has_location_or_home_town is True, 'Cannot get query without location or home_town'

        country_request = None

        if self.country:
            country_request = f'{self.country}, '

        location_query = self.location

        if not location_query:
            location_query = self.home_town

        if country_request:
            location_query = country_request + location_query

        return location_query

    def get_geo_query_structured(self) -> dict:
        """
        Get query for geocoding in structured representation
        @return:
        """
        assert self.has_location_or_home_town is True, 'Cannot get structured query without location or home_town'

        result = {}

        if self.country:
            result['country'] = self.country

        if self.location:
            result['city'] = self.location

        if self.home_town and 'city' not in result:
            result['city'] = self.home_town

        return result

    def identify_location(self, force: bool = False, structured_mode=False) -> bool:
        """
        Identify location for profile using geocoding and profile data (location, home_town, country)

        @note This method is not idempotent, it will change location_point, location_known and location_precise fields
        @param force: Force location discovery. Typically, we don't want to force geocoding if location is already known
        @param structured_mode: Use structured geocoding instead of plain text
        @return: True if location was found, False otherwise
        """
        if not force:
            if self.country is not None and self.country != 'Украина':
                return False

            # Already known
            if self.location_known:
                logger.debug('Location already known')
                return True

        # We cannot found location without at least approximate
        if not self.has_location_or_home_town:
            logger.warning(f'Cannot determine location without "location" or "home_town" for id={self.id}')
            return False

        if structured_mode:
            location_query = self.get_geo_query_structured()
        else:
            location_query = self.get_geo_query()

        coder = GeoCoderHelper()
        lookup_result = coder.geocode(query=location_query, country_codes=LOOKUP_COUNTRY_CODES)
        if lookup_result:
            logger.info(f'Request "{location_query}" resolved to "{lookup_result}"')
            self.location_point = lookup_result.point
            self.location_known = True
            self.location_precise = self.has_country
            return True

        # logger.info(f'Profile location was not found for query "{location_query}"')
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
