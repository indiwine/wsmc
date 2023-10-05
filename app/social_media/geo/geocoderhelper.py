import dataclasses
import hashlib
import logging
from enum import Enum
from time import sleep
from typing import Optional, Union, List, Callable, Dict, TypedDict

import geopy.exc
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.core.cache import cache
from geopy import Location
from geopy import Nominatim

from social_media.common import dataclass_asdict_skip_none

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class GeoCoderLookup:
    location: Location
    point: Point
    geometry: Optional[GEOSGeometry]

    def __str__(self):
        return f'Location: {self.location.address}'


class GeoCoderSource(Enum):
    LOCAL = 'local'
    REMOTE = 'remote'


class GeoCoderFeatureType(Enum):
    country = 'country'
    state = 'state'
    city = 'city'
    settlement = 'settlement'


@dataclasses.dataclass
class GeoCoderQuery:
    """
    Represents nominatim structured query
    """
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postalcode: Optional[str] = None

    def __str__(self):
        return f'GeoCoderQuery: {self.street} {self.city} {self.county} {self.state} {self.country} {self.postalcode}'

    def to_dict(self):
        return dataclass_asdict_skip_none(self)


class LocationAddressDetails(TypedDict):
    country: str
    country_code: str


class GeoCoderHelper:
    _geocoders: Dict[GeoCoderSource, Nominatim] = {}

    def __init__(self, source: GeoCoderSource = GeoCoderSource.LOCAL):
        self.source = source

    @classmethod
    def _build_geocoder_inst(cls, type: GeoCoderSource):
        if type not in cls._geocoders:
            if type == GeoCoderSource.LOCAL:
                nominatim_kwargs = {
                    'domain': settings.NOMINATIM_DOMAIN,
                    'user_agent': settings.NOMINATIM_USER_AGENT,
                    'timeout': settings.NOMINATIM_TIMEOUT,
                    'scheme': 'http'
                }
            elif type == GeoCoderSource.REMOTE:
                nominatim_kwargs = {
                    'user_agent': settings.NOMINATIM_USER_AGENT,
                    'timeout': settings.NOMINATIM_TIMEOUT,
                }
            else:
                raise RuntimeError(f'Unknown geocoder type: {type}')

            cls._geocoders[type] = Nominatim(**nominatim_kwargs)

        return cls._geocoders[type]

    def geocode(self,
                query: Union[str, GeoCoderQuery],
                country_codes: Union[str, List[str]] = None,
                max_retries: int = 10,
                delay: int = 15,
                featuretype: Optional[GeoCoderFeatureType] = None,
                include_geometry: bool = True,
                response_language: str = 'ru',
                namedetails: bool = False,
                addressdetails: bool = False,
                ) -> Optional[GeoCoderLookup]:

        hash_str = str(query)
        cache_key = (f'nominatium_location_{hashlib.md5(hash_str.encode()).hexdigest()}_'
                     f'{"_".join(country_codes) if country_codes else ""}_{featuretype.value if featuretype else ""}'
                     f'_{response_language}_{include_geometry}_{namedetails}_{addressdetails}')

        cache_item = cache.get(cache_key)

        if cache_item is None:

            lookup_result = self.restartable_gecode(lambda: self._build_geocoder_inst(self.source).geocode(
                query=query if isinstance(query, str) else query.to_dict(),
                geometry='wkt' if include_geometry else None,
                language=response_language,
                country_codes=country_codes,
                featuretype=featuretype.value if featuretype else None,
                namedetails=namedetails,
                addressdetails=addressdetails
            ), base_delay=delay, max_retries=max_retries)
            if not lookup_result:
                lookup_result = False

            cache.set(cache_key, lookup_result, 24 * 60 * 60)


        else:
            lookup_result = cache_item

        if lookup_result:
            return GeoCoderLookup(
                location=lookup_result,
                point=Point(lookup_result.longitude, lookup_result.latitude),
                geometry=GEOSGeometry(lookup_result.raw['geotext']) if 'geotext' in lookup_result.raw else None
            )

        return None

    def gecode_country(self, query: Union[str, GeoCoderQuery], response_language: str = 'ru') \
        -> Optional[LocationAddressDetails]:
        lookup_result = self.geocode(query,
                                     featuretype=GeoCoderFeatureType.country,
                                     include_geometry=False,
                                     response_language=response_language,
                                     addressdetails=True)
        if lookup_result and 'address' in lookup_result.location.raw:
            return LocationAddressDetails(
                **lookup_result.location.raw['address']
            )

        return None

    @staticmethod
    def restartable_gecode(cb: Callable, base_delay: int, max_retries: int) -> Location:
        for attempt in range(max_retries):
            try:
                return cb()
            except geopy.exc.GeocoderUnavailable:
                if (attempt + 1) == max_retries:
                    raise

                delay = base_delay * 2 ** attempt

                logger.error(f'Geocoder attempt {attempt + 1} failed failed, retry in {delay}s')
                sleep(delay)

    @staticmethod
    def normalize_to_multipolygon(lookup: GeoCoderLookup):
        if not lookup.geometry:
            return

        if lookup.geometry.geom_type == 'Polygon':
            lookup.geometry = MultiPolygon(lookup.geometry)
        elif lookup.geometry.geom_type == 'MultiPolygon':
            return
        else:
            raise RuntimeError(f'Cannot normalize geometry type of "{lookup.geometry.geom_type}" ')
