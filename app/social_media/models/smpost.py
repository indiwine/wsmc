from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models import Model, ForeignKey, CASCADE, TextField, DateTimeField, URLField, CharField, JSONField, Index

from .smprofile import SmProfile
from .suspect import Suspect
from ..social_media import SocialMediaTypes


class SmPost(Model):
    suspect = ForeignKey(Suspect, on_delete=CASCADE, verbose_name='Людина')
    sm_post_id = CharField(max_length=25000, help_text='ID поста в соціальній мережі', verbose_name='ID',
                           editable=False)
    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices, verbose_name='Соціальна мережа')
    datetime = DateTimeField(verbose_name='Час створення', help_text='Час коли пост було створено в соціальній мережі')

    body = TextField(null=True, verbose_name='Текст')
    permalink = URLField(null=True, help_text='Прямий лінк на пост', max_length=2512, editable=False)
    raw_post = JSONField(null=True, editable=False)
    search_vector = SearchVectorField('body', editable=False)
    profile = ForeignKey(SmProfile, on_delete=CASCADE, verbose_name='Профіль',
                         help_text="Профіль зв'язаний з цим постом")

    def __str__(self):
        post = self.sm_post_id[0:20]
        if self.body:
            post = self.body[0:20]

        return f'Пост {post}'

    class Meta:
        indexes = [
            Index(fields=['sm_post_id', 'social_media', 'profile', 'datetime', 'suspect']),
            GinIndex(
                SearchVector('search_vector', config='russian'),
                name='search_vector_idx'
            )
        ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Пости'
