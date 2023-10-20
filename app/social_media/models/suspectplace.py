from asgiref.sync import sync_to_async
from django.db import models

from .country import Country


class SuspectPlace(models.Model):
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    city = models.CharField(max_length=255, verbose_name='Місто (російською)')
    place_collected = models.BooleanField(default=False, verbose_name='Місце зібрано')

    def __str__(self):
        return f'{self.city}, {self.country}'

    @sync_to_async
    def aget_location(self):
        return f'{self.city}, {self.country}'
