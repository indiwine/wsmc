from __future__ import annotations

from typing import List

from django.core.exceptions import EmptyResultSet
from django.db import models, transaction
from encrypted_model_fields.fields import EncryptedCharField

from social_media.social_media.socialmediatypes import SocialMediaTypes


class SmCredentialManager(models.Manager):
    def get_next_credential(self, social_media: SocialMediaTypes) -> SmCredential:
        """
        Find next suitable credential based on a round-robin algorithm

        @raise EmptyResultSet in case if no relevant credentials can be found
        @param social_media:
        @return:
        """
        credentials = self.select_for_update().filter(social_media=social_media, in_use=True).order_by('id')
        with transaction.atomic():
            credential_list: List[SmCredential] = list(credentials)
            numbof_credentials = len(credential_list)
            if numbof_credentials == 0:
                raise EmptyResultSet(f'Cannot find any credentials for "{social_media}"')

            def extract_and_update(index_in_list):
                used_credential = credential_list[index_in_list]
                used_credential.was_last_used = True
                used_credential.save()
                return used_credential

            for index, credential in enumerate(credential_list):
                if credential.was_last_used:
                    next_index = index + 1

                    if next_index + 1 > numbof_credentials:
                        next_index = 0

                    self.filter(social_media=social_media).update(was_last_used=False)

                    next_credential = extract_and_update(next_index)
                    return next_credential

            return extract_and_update(0)


class SmCredential(models.Model):
    objects = SmCredentialManager()
    user_name = models.CharField(max_length=255)
    password = EncryptedCharField(max_length=255)
    social_media = models.CharField(
        max_length=4,
        choices=SocialMediaTypes.choices,
        default=SocialMediaTypes.FB)

    was_last_used = models.BooleanField(default=False, editable=False)
    last_used_date = models.DateTimeField(null=True, default=None, editable=False)
    in_use = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user_name} ({self.get_social_media_display()})'

    class Meta:
        verbose_name = 'Аккаунт соціальної мережі'
        verbose_name_plural = 'Аккаунти соціальних мереж'
