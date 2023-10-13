import cProfile
from typing import List
from unittest.mock import MagicMock

from django.conf import settings
from django.test import TestCase

from social_media.models import SmCredential, SuspectGroup, SmProfile, VkPostStat
from social_media.social_media import SocialMediaTypes, SocialMediaActions
from social_media.webdriver import Agent
from social_media.webdriver.collectors import Collector
from social_media.webdriver.collectors.vk import VkLoginCollector
from social_media.webdriver.collectors.vk.vkgroupcollector import VkGroupCollector
from social_media.webdriver.collectors.vk.vkpostscollector import VkPostsCollector
from social_media.webdriver.collectors.vk.vksecondaryprofilescollector import VkSecondaryProfilesCollector
from social_media.webdriver.options.vkoptions import VkOptions
from social_media.webdriver.request import Request


class TestVkCollectors(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credential = SmCredential.objects.create(
            user_name=settings.TEST_VK_LOGIN,
            password=settings.TEST_VK_PASSWORD,
            social_media=SocialMediaTypes.VK
        )

    def create_agent(self, request: Request, filter_stack: List[Collector]):
        run_agent = Agent(request)
        for collector in filter_stack:
            collector.set_options(request.options)

        run_agent.construct_filter_stack = MagicMock(return_value=filter_stack)
        return run_agent

    async def test_login(self):
        request = Request([SocialMediaActions.LOGIN], credentials=self.credential)
        request.driver_build_options.block_images = False
        request.driver_build_options.profile_folder_name = None
        request.options.login_use_jitter = False

        login_collector = VkLoginCollector()

        run_agent = self.create_agent(request, [login_collector])
        await run_agent.run()
        # Here we gustls assume login is successfully if there is no errors

    async def test_group_collector(self):
        suspect_group = await SuspectGroup.objects.acreate(
            url='https://vk.com/jj.crocodile',
        )

        request = Request(
            actions=[
                SocialMediaActions.LOGIN,
                SocialMediaActions.GROUP,
                SocialMediaActions.POSTS
            ],
            credentials=self.credential,
            suspect_identity=suspect_group
        )

        def mock_offset_generator(a, b, c):
            for offset in [0]:
                yield offset

        posts_collector = VkPostsCollector()

        posts_collector.offset_generator = MagicMock(side_effect=mock_offset_generator)

        collector_stack = [
            VkLoginCollector(),
            VkGroupCollector(),
            posts_collector,
        ]

        run_agent = self.create_agent(request, collector_stack)
        await run_agent.run(max_retries=1)
        saved_group = await posts_collector.aget_request_origin(request)

        # Todo: fix this test
        # self.assertEqual(suspect_group.id, saved_group.suspect_group.id)

    async def test_secondary_collector(self):
        original_profile = await SmProfile.objects.acreate(
            oid='1',
            credentials=self.credential,
            name='',
            social_media=SocialMediaTypes.VK
        )
        request = Request([], credentials=self.credential)
        run_agent = self.create_agent(request, [VkSecondaryProfilesCollector()])
        await run_agent.run(max_retries=1)

        updated_profile = await SmProfile.objects.aget(id=original_profile.id)
        self.assertTrue(updated_profile.name)
        self.assertTrue(updated_profile.location)
        self.assertTrue(updated_profile.was_collected)
        self.assertTrue(updated_profile.birthdate)
        self.assertTrue(updated_profile.university)
        self.assertEqual(self.credential.id, updated_profile.credentials_id)
        self.assertIsNone(updated_profile.suspect_social_media)

    def test_post_offset_generator(self):
        VkPostsCollector.MIN_PROFILES_PER_REQUEST = 1
        posts_collector = VkPostsCollector()
        posts_collector.MIN_PROFILES_PER_REQUEST = 1

        options = VkOptions()
        posts_collector.set_options(options)

        suspect_group = SuspectGroup.objects.create(
            url='https://vk.com/jj.crocodile',
        )

        request = Request(
            actions=[
                SocialMediaActions.POSTS
            ],
            credentials=self.credential,
            suspect_identity=suspect_group
        )

        new_amount = MagicMock(return_value=0)

        steps = 4
        max_offset = VkPostsCollector.STEP * steps

        offsets = posts_collector.offset_generator(request, new_amount, max_offset)

        def steps_to_offset_cb(item):
            return item * VkPostsCollector.STEP

        # Normal flow
        expected_offsets = map(steps_to_offset_cb, range(steps + 1))
        self.assertSequenceEqual(list(offsets), list(expected_offsets))

        collected_step = 3
        collected_offset = VkPostsCollector.STEP * collected_step
        post_stat_obj = VkPostStat.objects.create(
            suspect_group=suspect_group,
            last_offset=collected_offset
        )

        # Flow with the existing position
        offsets = posts_collector.offset_generator(request, new_amount, max_offset)
        expected_offsets = [0] + list(map(steps_to_offset_cb, range(collected_step, steps + 1)))
        self.assertSequenceEqual(list(offsets), expected_offsets)

        steps += 1
        max_offset = VkPostsCollector.STEP * steps

        new_amount_calls = 0

        def amount_cb():
            nonlocal new_amount_calls
            new_amount_calls += 1

            if new_amount_calls == 1:
                return VkPostsCollector.STEP
            return 0

        offsets = posts_collector.offset_generator(request, amount_cb, max_offset)
        expected_offsets = list(map(steps_to_offset_cb, range(2))) + \
                           list(map(steps_to_offset_cb, range(collected_step + 1, steps + 1)))
        self.assertSequenceEqual(list(offsets), expected_offsets)

        # Flow with the direct retry
        options.configure_for_retry()
        offsets = posts_collector.offset_generator(request, amount_cb, max_offset)
        expected_offsets = map(steps_to_offset_cb, range(collected_step, steps + 1))
        self.assertSequenceEqual(list(offsets), list(expected_offsets))
