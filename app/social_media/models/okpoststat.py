from django.db.models import Model, CASCADE, PositiveIntegerField, OneToOneField, CharField

from social_media.models.suspectsocialmediaaccount import SuspectSocialMediaAccount
from social_media.models.suspectgroup import SuspectGroup
from .suspectplace import SuspectPlace


class OkPostStat(Model):
    suspect_social_media = OneToOneField(SuspectSocialMediaAccount, on_delete=CASCADE, null=True)
    suspect_group = OneToOneField(SuspectGroup, on_delete=CASCADE, null=True)
    suspect_place = OneToOneField(SuspectPlace, on_delete=CASCADE, null=True)
    last_offset = PositiveIntegerField()
    last_anchor = CharField(max_length=512)

    class Meta:
        verbose_name = 'Статистика ОК'
        verbose_name_plural = 'Статистика ОК'
