from django.db.models import Model, CharField, ManyToManyField
from .location import Location

class SmProfileLocationFilter(Model):
    name = CharField(max_length=128)

    locations = ManyToManyField(Location)

    def __str__(self):
        return self.name
