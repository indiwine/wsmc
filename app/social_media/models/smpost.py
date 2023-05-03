from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models import Model, ForeignKey, CASCADE, TextField, DateTimeField, URLField, CharField, JSONField, \
    Index, PositiveIntegerField

from .smlikes import SmLikes
from .smprofile import SmProfile
from ..social_media import SocialMediaTypes


class SmPost(Model):
    permalink = URLField(null=True, help_text='Прямий лінк на пост', max_length=2512, editable=False)

    author_type = ForeignKey(ContentType, on_delete=CASCADE, related_name='author')
    author_id = PositiveIntegerField(verbose_name='')
    author_object = GenericForeignKey('author_type', 'author_id')
    """Post author"""

    origin_type = ForeignKey(ContentType, on_delete=CASCADE, related_name='origin')
    origin_id = PositiveIntegerField(verbose_name='')
    origin_object = GenericForeignKey('origin_type', 'origin_id')
    """Post origin, typically group or user """

    # TODO: Removal
    # suspect = ForeignKey(Suspect, on_delete=CASCADE, verbose_name='Людина')
    # profile = ForeignKey(SmProfile, on_delete=CASCADE, verbose_name='Профіль',
    #                      help_text="Профіль зв'язаний з цим постом")

    likes = GenericRelation(SmLikes,
                            object_id_field='parent_id',
                            content_type_field='parent_type'
                            )

    sm_post_id = CharField(max_length=25000, help_text='ID поста в соціальній мережі', verbose_name='ID',
                           editable=False)

    social_media = CharField(max_length=4, choices=SocialMediaTypes.choices, verbose_name='Соціальна мережа')

    datetime = DateTimeField(verbose_name='Час створення', help_text='Час коли пост було створено в соціальній мережі')

    body = TextField(null=True, verbose_name='Текст')

    raw_post = JSONField(null=True, editable=False)
    search_vector = SearchVectorField('body', editable=False)

    def __str__(self):
        post = self.sm_post_id[0:20]
        if self.body:
            post = self.body[0:20]

        return f'Пост {post}'

    class Meta:
        unique_together = ['sm_post_id', 'social_media']
        indexes = [
            Index(fields=[
                'sm_post_id',
                'social_media',
                'datetime',
                'origin_type',
                'origin_id',
                'author_type',
                'author_id'
            ]),
            GinIndex(
                SearchVector('search_vector', config='russian'),
                name='search_vector_idx'
            )
        ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Пости'
