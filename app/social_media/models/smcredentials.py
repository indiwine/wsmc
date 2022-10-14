from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

from social_media.social_media.socialmediatypes import SocialMediaTypes


class SmCredentials(models.Model):
    user_name = models.CharField(max_length=255)
    password = EncryptedCharField(max_length=255)
    social_media = models.CharField(
        max_length=4,
        choices=SocialMediaTypes.choices,
        default=SocialMediaTypes.FB)


    def __str__(self):
        return f'{self.user_name} ::> {self.social_media}'

    class Meta:
        verbose_name = 'Аккаунт соціальної мережі'
        verbose_name_plural = 'Аккаунти соціальних мереж'
