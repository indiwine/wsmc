from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, ForeignKey, CASCADE, PositiveIntegerField, JSONField, CharField, Index

from social_media.models.screeningreport import ScreeningReport
from social_media.screening import ScreeningModules


class ScreeningDetail(Model):
    report = ForeignKey(ScreeningReport, on_delete=CASCADE)
    content_type = ForeignKey(ContentType, on_delete=CASCADE)
    object_id = PositiveIntegerField(verbose_name='ID сутності')
    content_object = GenericForeignKey('content_type', 'object_id')
    result = JSONField()
    module = CharField(choices=ScreeningModules.choices, max_length=2, verbose_name='Модуль')

    class Meta:
        indexes = [
            Index(fields=['object_id', 'content_type', 'report', 'module'])
        ]
        verbose_name = 'Деталі перевірки соцмереж'
        verbose_name_plural = 'Деталі перевірки соцмереж'
