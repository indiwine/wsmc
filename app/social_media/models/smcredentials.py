from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

from social_media.social_media.social_media_types import social_media_model_choices, SocialMediaTypes, social_media_model_choices_dict


class SmCredentials(models.Model):
    user_name = models.CharField(max_length=255)
    password = EncryptedCharField(max_length=255)
    social_media = models.CharField(max_length=4, choices=social_media_model_choices, default=SocialMediaTypes.FB)

    def __str__(self):
        return f'{self.user_name} ::> {social_media_model_choices_dict[self.social_media]}'

    class Meta:
        verbose_name = 'Аккакунт соціальної мережі'
        verbose_name_plural = 'Аккакунти соціальних мереж'
