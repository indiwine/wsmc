from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Model, URLField, CharField, ForeignKey, SET_NULL, RESTRICT, Index

from .smcredential import SmCredential
from .smpost import SmPost
from .suspect_group import SuspectGroup


class SmGroup(Model):
    permalink = URLField()
    oid = CharField(max_length=25000)
    name = CharField(max_length=1024)

    suspect_group = ForeignKey(SuspectGroup, on_delete=SET_NULL, null=True)
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, editable=False)

    posts = GenericRelation(SmPost)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            Index(fields=['suspect_group', 'oid', 'credentials'])
        ]
