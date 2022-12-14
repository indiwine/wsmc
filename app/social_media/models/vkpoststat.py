from django.db.models import Model, CASCADE, PositiveIntegerField, OneToOneField

from social_media.models.suspectsocialmediaaccount import SuspectSocialMediaAccount


class VkPostStat(Model):
    suspect_social_media = OneToOneField(SuspectSocialMediaAccount, on_delete=CASCADE)
    last_offset = PositiveIntegerField()

    class Meta:
        verbose_name = 'Статистика ВК'
        verbose_name_plural = 'Статистика ВК'
