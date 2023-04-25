from django.db.models import Model, ForeignKey, CASCADE, PositiveIntegerField, Index
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .smprofile import SmProfile


class SmLikes(Model):
    # Identity who created "a like"
    owner = ForeignKey(SmProfile, on_delete=CASCADE)

    # Where like is attached to (post or comment)
    parent_type = ForeignKey(ContentType, on_delete=CASCADE)
    parent_id = PositiveIntegerField(verbose_name='ID сутності')
    parent_object = GenericForeignKey('parent_type', 'parent_id')

    class Meta:
        unique_together = ['owner', 'parent_type', 'parent_id']