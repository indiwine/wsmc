from django.core.exceptions import EmptyResultSet
from django.test import TestCase

from social_media.models import SmCredential
from social_media.social_media import SocialMediaTypes


class TestSmCredential(TestCase):
    creds = None

    @classmethod
    def setUpTestData(cls):
        cls.creds = [
            SmCredential(id=1, user_name='dummy_1', password='pass', social_media=SocialMediaTypes.VK),
            SmCredential(id=2, user_name='dummy_2', password='pass', social_media=SocialMediaTypes.VK),
            SmCredential(id=3, user_name='dummy_3', password='pass', social_media=SocialMediaTypes.VK),
            SmCredential(id=4, user_name='dummy_4', password='pass', social_media=SocialMediaTypes.VK, in_use=False),
        ]

        for cred in cls.creds:
            cred.save()

    def test_get_next_credential(self):
        for i in range(3):
            found_cred = SmCredential.objects.get_next_credential(SocialMediaTypes.VK)
            self.assertEqual(self.creds[i], found_cred)
        found_cred = SmCredential.objects.get_next_credential(SocialMediaTypes.VK)
        self.assertEqual(self.creds[0], found_cred)

    def test_empty_credentials(self):
        self.assertRaises(EmptyResultSet, SmCredential.objects.get_next_credential, SocialMediaTypes.FB)
