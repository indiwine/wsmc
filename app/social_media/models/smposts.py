from django.contrib.postgres.search import SearchVector
from django.db.models import Model, ForeignKey, CASCADE, TextField, DateTimeField, URLField, CharField, JSONField, Index

from . import Suspect
from .smprofile import SmProfile
from ..social_media import SocialMediaTypes


class SmPosts(Model):
    profile = ForeignKey(SmProfile, on_delete=CASCADE)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)
    sm_post_id = CharField(max_length=25000, help_text='ID поста в соціальній мережі')
    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices)
    datetime = DateTimeField(verbose_name='Час створення')

    body = TextField(null=True, verbose_name='Текст')
    permalink = URLField(null=True, help_text='Прямий лінк на пост')
    raw_post = JSONField(null=True)
    search_vector = SearchVector('body')

    def __str__(self):
        post = self.sm_post_id[0:20]
        if self.body:
            post = self.body[0:20]

        return f'Пост {post}'

    class Meta:
        indexes = [
            Index(fields=['sm_post_id', 'social_media', 'profile', 'datetime', 'suspect']),
        ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Пости'
