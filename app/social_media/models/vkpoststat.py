from django.db.models import Model, CASCADE, PositiveIntegerField, OneToOneField

from .suspectgroup import SuspectGroup
from .suspectsocialmediaaccount import SuspectSocialMediaAccount


class VkPostStat(Model):
    suspect_social_media = OneToOneField(SuspectSocialMediaAccount, on_delete=CASCADE, null=True)
    suspect_group = OneToOneField(SuspectGroup, on_delete=CASCADE, null=True)
    last_offset = PositiveIntegerField()

    class Meta:
        verbose_name = 'Статистика ВК'
        verbose_name_plural = 'Статистика ВК'
