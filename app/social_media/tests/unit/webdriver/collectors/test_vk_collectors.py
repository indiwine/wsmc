from unittest.mock import MagicMock

from django.conf import settings
from django.test import TestCase

from social_media.models import SmCredential, SuspectGroup, SmProfile
from social_media.social_media import SocialMediaTypes, SocialMediaEntities
from social_media.webdriver import Request, Agent
from social_media.webdriver.collectors import Collector
from social_media.webdriver.collectors.vk import VkLoginCollector
from social_media.webdriver.collectors.vk.vkgroupcollector import VkGroupCollector
from social_media.webdriver.collectors.vk.vkpostscollector import VkPostsCollector
from social_media.webdriver.collectors.vk.vksecondaryprofilescollector import VkSecondaryProfilesCollector


class TestVkCollectors(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credential = SmCredential.objects.create(
            user_name=settings.TEST_VK_LOGIN,
            password=settings.TEST_VK_PASSWORD,
            social_media=SocialMediaTypes.VK
        )

    def create_agent(self, request: Request, chain_obj: Collector):
        run_agent = Agent(request)
        run_agent._construct_chain = MagicMock(return_value=chain_obj)
        return run_agent

    def test_login(self):
        request = Request([SocialMediaEntities.LOGIN], credentials=self.credential)
        run_agent = self.create_agent(request, VkLoginCollector())
        run_agent.run()
        # Here we gust assume login is successfully if there is no errors

    def test_group_collector(self):
        suspect_group = SuspectGroup.objects.create(
            name='Test Vk Group',
            url='https://vk.com/jj.crocodile',
            credentials=self.credential
        )

        request = Request(
            entities=[
                SocialMediaEntities.GROUP,
                SocialMediaEntities.POSTS
            ],
            credentials=self.credential,
            suspect_identity=suspect_group
        )

        def mock_offset_generator(a, b):
            for offset in [0]:
                yield offset

        posts_collector = VkPostsCollector()
        posts_collector.offset_generator = MagicMock(side_effect=mock_offset_generator)

        group_collector = VkGroupCollector().set_next(posts_collector)
        run_agent = self.create_agent(request, group_collector)
        run_agent.run()
        saved_group = posts_collector.get_request_origin(request)

        self.assertEqual(suspect_group.id, saved_group.suspect_group.id)

    def test_secondary_collector(self):
        original_profile = SmProfile.objects.create(
            oid='1',
            credentials=self.credential,
            name='',
            social_media=SocialMediaTypes.VK
        )
        request = Request([], credentials=self.credential)
        run_agent = self.create_agent(request, VkSecondaryProfilesCollector())
        run_agent.run()

        updated_profile = SmProfile.objects.get(id=original_profile.id)
        self.assertTrue(updated_profile.name)
        self.assertTrue(updated_profile.location)
        self.assertTrue(updated_profile.was_collected)
        self.assertTrue(updated_profile.birthdate)
        self.assertTrue(updated_profile.university)
        self.assertEqual(self.credential.id, updated_profile.credentials_id)
        self.assertIsNone(updated_profile.suspect_social_media)
