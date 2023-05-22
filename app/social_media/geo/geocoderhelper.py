import dataclasses
import hashlib
import logging
from typing import Optional, Union, List, Callable

import geopy.exc
from django.core.cache import cache

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from geopy import Location
from geopy import Nominatim


logger = logging.getLogger(__name__)

@dataclasses.dataclass
class GeoCoderLookup:
    location: Location
    point: Point
    geometry: Optional[GEOSGeometry]



class GeoCoderHelper:
    _GEOCODER_INST: Optional[Nominatim] = None

    @classmethod
    def get_geocoder_inst(cls):
        if cls._GEOCODER_INST is None:
            cls._GEOCODER_INST = Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)

        return cls._GEOCODER_INST

    def geocode(self,
                query: Union[str],
                country_codes: Union[str, List[str]] = None,
                max_retries: int = 10,
                delay: int = 60) -> Optional[GeoCoderLookup]:

        cache_key = f'nominatium_location_{hashlib.md5(query.encode()).hexdigest()}'

        cache_item = cache.get(cache_key)

        lookup_result: Optional[Union[Location, False]] = None

        if cache_item is None:
            for attempt in range(max_retries):
                try:
                    lookup_result = self.restartable_gecode(lambda: self.get_geocoder_inst().geocode(
                        query=query,
                        geometry='wkt',
                        language='ru',
                        country_codes=country_codes
                    ), delay=delay, max_retries=max_retries)


                    if not lookup_result:
                        lookup_result = False

                    cache.set(cache_key, lookup_result, 24 * 60 * 60)
                except geopy.exc.GeocoderUnavailable:

                    logger.error('Geocoder attempt failed failed')


        else:
            lookup_result = cache_item

        if lookup_result:
            return GeoCoderLookup(
                location=lookup_result,
                point=Point(lookup_result.longitude, lookup_result.latitude),
                geometry=GEOSGeometry(lookup_result.raw['geotext']) if 'geotext' in lookup_result.raw else None
            )

        return None
    @staticmethod
    def restartable_gecode(cb: Callable, delay: int, max_retries: int) -> Location:
        for attempt in range(max_retries):
            try:
                return cb()
            except geopy.exc.GeocoderUnavailable:
                if (attempt + 1) == max_retries:
                    raise

                logger.error(f'Geocoder attempt {attempt + 1} failed failed, retry in {delay}s')
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
