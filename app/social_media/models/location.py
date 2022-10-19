from typing import Optional

import geopandas
from django.conf import settings
from django.db.models import Model, CharField, JSONField, PositiveIntegerField, BooleanField
from geopy import Location as GeoPyLocation
from geopy.geocoders import Nominatim
from shapely.geometry import Point

from social_media.exceptions import LocationRequestInvalidError


class Location(Model):
    name = CharField(max_length=1024, verbose_name='Назва')
    weight = PositiveIntegerField(default=0, verbose_name='Вага',
                                  help_text='Чим більша вага, тим більш підозріле місце знаходження')
    location_data = JSONField(editable=False, null=True)
    is_valid = BooleanField(default=False, verbose_name='Коректна Локація?',
                            help_text='Чи може бути використана ця локація для ідентифікації')

    class Meta:
        verbose_name = 'Локація'
        verbose_name_plural = 'Локації'

    def __str__(self):
        return self.name

    @property
    def get_geo_data_frame(self) -> Optional[geopandas.GeoDataFrame]:
        dataframe = None
        if self.is_valid:
            gs = geopandas.GeoSeries.from_wkt([self.location_data['geotext']])
            dataframe = geopandas.GeoDataFrame({'BoroName': [self.name]}, geometry=gs, crs="EPSG:4326")
            dataframe.set_index("BoroName")

        return dataframe

    def having_same_location(self, request_location: str) -> bool:
        """
        Check if or location inside the same lo
        @param request_location:
        @return: bool
        @raise LocationRequestInvalidError - if request_city cannot be found
        @raise RuntimeError - if location is invalid
        """
        point, _ = self.get_point(request_location)
        return self.intersects_with_point(point)

    def intersects_with_point(self, point: Point) -> bool:
        if not self.is_valid:
            raise RuntimeError(f'Trying to check against invalid location')
        return self.get_geo_data_frame.intersects(point).bool()

    @staticmethod
    def get_point(request_location: str) -> tuple[Point, GeoPyLocation]:
        """
        Try to get point out of text
        @param request_location:
        @return:
        @raise LocationRequestInvalidError
        """
        geocoder = Location._get_geocoder()
        geolocation: GeoPyLocation = geocoder.geocode({'city': request_location})
        if not geolocation:
            geolocation = geocoder.geocode(request_location)

        if not geolocation:
            raise LocationRequestInvalidError(f'Location request: "{request_location}" could not be found')

        return Point(geolocation.longitude, geolocation.latitude), geolocation

    @staticmethod
    def _get_geocoder() -> Nominatim:
        return Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)

    def save(
            self, *args, **kwargs
    ):

        geolocator = self._get_geocoder()
        real_location: GeoPyLocation = geolocator.geocode(self.name, geometry='wkt')

        if real_location:
            self.name = real_location.address
            self.location_data = real_location.raw
            if 'geotext' in self.location_data:
                self.is_valid = True

        return super().save(*args, **kwargs)
