from django.test import TestCase

from social_media.dtos import SmProfileDto
from social_media.models import SmCredential, SmProfile
from social_media.social_media import SocialMediaTypes
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.request import Request
from wsmc import settings


class DummyCollector(AbstractCollector):
    async def handle(self, request: Request):
        pass


class TestBasicCollector(TestCase):
    """
    Test case for AbstractCollector class
    """

    @classmethod
    def setUpTestData(cls):
        cls.credential = SmCredential.objects.create(
            user_name=settings.TEST_OK_LOGIN,
            password=settings.TEST_OK_PASSWORD,
            social_media=SocialMediaTypes.OK
        )

    def setUp(self) -> None:
        # Since AbstractCollector is an abstract class, we need to use a concrete implementation
        self.collector = DummyCollector()
        self.request = Request([], credentials=self.credential)

    def test_update_collected_profiles(self):
        """
        Test that update_collected_profiles() method works correctly
        """
        junk_profile = SmProfileDto(
            name='junk',
            oid='123',
            country='Russia'
        )

        ok_profile = SmProfileDto(
            name='ok',
            oid='456',
            country='Ukraine',
            location='Kiev'
        )

        self.collector.persist_sm_profile(junk_profile, self.request)
        self.collector.persist_sm_profile(ok_profile, self.request)
        self.collector.update_collected_profiles([junk_profile, ok_profile], self.request)
        self.assertTrue(SmProfile.objects.filter(oid=ok_profile.oid, in_junk=False).exists(), 'OK profile should be saved')
        self.assertTrue(SmProfile.objects.filter(oid=junk_profile.oid, in_junk=True).exists(), 'Junk profile should be saved')
