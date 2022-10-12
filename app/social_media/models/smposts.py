from django.db.models import Model, ForeignKey, CASCADE, TextField, DateTimeField, URLField, CharField, JSONField, Index

from . import Suspect
from .smprofile import SmProfile
from ..social_media import SocialMediaTypes


class SmPosts(Model):
    profile = ForeignKey(SmProfile, on_delete=CASCADE)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)
    sm_post_id = CharField(max_length=2048, help_text='ID поста в соціальній мережі')
    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices)
    datetime = DateTimeField()

    body = TextField(null=True)
    permalink = URLField(null=True, help_text='Прямий лінк на пост')
    raw_post = JSONField(null=True)

    class Meta:
        indexes = [
            Index(fields=['sm_post_id', 'social_media', 'profile', 'datetime', 'suspect']),
        ]
