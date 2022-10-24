from django.db.models import Model, CASCADE, PositiveIntegerField, OneToOneField

from social_media.models.suspectsocialmediaaccount import SuspectSocialMediaAccount


class VkPostStat(Model):
    suspect_social_media = OneToOneField(SuspectSocialMediaAccount, on_delete=CASCADE)
    last_offset = PositiveIntegerField()
