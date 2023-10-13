from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Model, URLField, CharField, ForeignKey, SET_NULL, RESTRICT, Index, BooleanField

from .smcredential import SmCredential
from .smpost import SmPost
from .suspectgroup import SuspectGroup
from ..social_media import SocialMediaTypes


class SmGroup(Model):
    permalink = URLField()
    oid = CharField(max_length=25000)
    name = CharField(max_length=1024)

    suspect_group = ForeignKey(SuspectGroup, on_delete=SET_NULL, null=True)
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, editable=False)
    posts_collected = BooleanField(default=False, editable=False)
    
    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices, verbose_name='Соціальна мережа')

    posts = GenericRelation(SmPost)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['oid', 'social_media']
        indexes = [
            Index(fields=['suspect_group', 'oid', 'credentials', 'social_media'])
        ]
