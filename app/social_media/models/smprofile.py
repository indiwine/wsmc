import logging
from typing import Optional

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db.models import PointField
from django.db.models import Model, ForeignKey, RESTRICT, CharField, DateField, Index, BooleanField, SET_NULL, \
    JSONField, Q
from django.db.transaction import atomic
from tinymce.models import HTMLField

from .country import Country
from .smcredential import SmCredential
from .suspectsocialmediaaccount import SuspectSocialMediaAccount
from ..geo.geocoderhelper import GeoCoderHelper, GeoCoderQuery, GeoCoderSource
from ..social_media import SocialMediaTypes
from ..social_media.profileauthenticitystatus import ProfileAuthenticityStatus
from ..social_media.profilescreeningstatus import ProfileScreeningStatus

logger = logging.getLogger(__name__)

LOOKUP_COUNTRY_CODES = ['UA']


class SmProfile(Model):
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, editable=False)
    suspect_social_media = ForeignKey(SuspectSocialMediaAccount, on_delete=SET_NULL, null=True, editable=False)
    country_ref = ForeignKey(Country, on_delete=RESTRICT, null=True, editable=False, default=None)

    oid = CharField(max_length=512, verbose_name='ID', help_text='ID користувача в соціальній мережі')
    name = CharField(max_length=512, verbose_name="Ім'я", help_text="Ім'я як вказано в соціальній мережі")
    university = CharField(max_length=512, null=True, verbose_name='Освіта')
    location = CharField(max_length=512, null=True, verbose_name='Місце проживання')
    home_town = CharField(max_length=512, null=True, verbose_name='Місце народження')
    birthdate = DateField(null=True, verbose_name="Дата народження",
                          help_text='Може бути вказаний поточний рік у випадку якщо рік не вказан в соц мережі')

    domain = CharField(max_length=512, null=True)
    metadata = JSONField(null=True)

    was_collected = BooleanField(default=False)

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

    in_junk = BooleanField(default=False, editable=False)

    is_wall_available = BooleanField(default=True, editable=False)
    posts_collected = BooleanField(default=False)

    authored_posts = GenericRelation(
        'SmPost',
        object_id_field='author_id',
        content_type_field='author_type',
        related_query_name='author',
        editable=False
    )

    wall = GenericRelation(
        'SmPost',
        object_id_field='origin_id',
        content_type_field='origin_type',
        related_query_name='wall',
        editable=False
    )

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
        return bool(self.country_ref_id)

    @property
    def should_be_kept(self) -> bool:
        return self.has_country and self.location_known and self.country_ref.code in settings.WSMC_PROFILE_COUNTRIES_TO_KEEP

    def move_to_junk(self):
        """
        Move profile to junk
        Removes all associated data as well (likes, posts, comments, etc)
        Removal done inside the transaction
        @return:
        """
        from .smcomment import SmComment
        from .smlikes import SmLikes
        from .smpost import SmPost
        with atomic():
            SmLikes.objects.filter(owner=self).delete()
            SmPost.objects.filter(
                Q(author=self) | Q(wall=self)
            ).delete()
            SmComment.objects.filter(owner=self).delete()

            self.in_junk = True
            self.save()

    def resolve_country_ref(self, country_name: Optional[str]):
        """
        Resolve country reference by name and set appropriate field
        @param country_name:
        @return: True if country was found, False otherwise
        """
        if not country_name:
            logger.debug('Country name is empty')
            return False

        if len(country_name) == 0:
            logger.debug('Country name is empty')
            return False

        query = GeoCoderQuery(country=country_name)
        coder = GeoCoderHelper(source=GeoCoderSource.REMOTE)
        lookup_result = coder.gecode_country(query=query)
        if not lookup_result:
            logger.debug(f'Country "{country_name}" was not found')
            self.country_ref = None
            return False

        self.country_ref, _ = Country.objects.get_or_create(code=lookup_result['country_code'], defaults={
            'name': lookup_result['country'],
            'code': lookup_result['country_code'],
        })

        logger.debug(f'Country "{country_name}" was resolved to "{self.country_ref}"')

        return True

    def get_geo_query(self) -> str:
        """
        Get query for geocoding in plain text representation
        @return:
        """
        return self.get_geo_query_structured().to_query_string()

    def get_geo_query_structured(self) -> GeoCoderQuery:
        """
        Get query for geocoding in structured representation
        @return:
        """
        assert self.has_location_or_home_town is True, 'Cannot get structured query without location or home_town'

        result = GeoCoderQuery()

        if self.has_country:
            result.country = self.country_ref.name

        if self.location:
            result.city = self.location

        if self.home_town and result.city is None:
            result.city = self.home_town

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
            if not self.has_country:
                return False

            # Already known
            if self.location_known:
                logger.debug('Location already known')
                return True

        # We cannot found location without at least approximate
        if not self.has_location_or_home_town:
            logger.debug(f'Cannot determine location without "location" or "home_town" for id={self.id}')
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
                'oid',
                'was_collected',
                'social_media',
                'in_junk',
                'screening_status',
                'authenticity_status',
                'posts_collected'
            ])
        ]
