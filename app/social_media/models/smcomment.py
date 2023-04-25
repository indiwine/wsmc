from django.db.models import Model, CASCADE, ForeignKey, DateTimeField, TextField, CharField, \
    Index
from django.contrib.contenttypes.fields import GenericRelation

from .smpost import SmPost
from .smlikes import SmLikes
from .smprofile import SmProfile


class SmComment(Model):
    owner = ForeignKey(SmProfile, on_delete=CASCADE)
    """Identity who created a comment"""

    post = ForeignKey(SmPost, on_delete=CASCADE)

    parent_comment = ForeignKey('self', on_delete=CASCADE, null=True, default=None)
    """Actual parent (if any)"""

    datetime = DateTimeField(verbose_name='Час створення', help_text='Час коли пост було створено в соціальній мережі')
    body = TextField(null=True, verbose_name='Текст')

    oid = CharField(max_length=25000, help_text='ID поста в соціальній мережі', verbose_name='ID',
                    editable=False)

    likes = GenericRelation(SmLikes,
                            object_id_field='parent_id',
                            content_type_field='parent_type'
                            )

    class Meta:
        indexes = [
            Index(fields=['owner', 'oid', 'parent_comment', 'post'])
        ]
