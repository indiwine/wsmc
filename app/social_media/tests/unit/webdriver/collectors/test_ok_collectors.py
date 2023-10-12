from pprint import pprint

from django.conf import settings
from django.test import TestCase

from social_media.models import SmCredential, SuspectGroup, SmGroup, Suspect, SuspectSocialMediaAccount, SuspectPlace, \
    Country
from social_media.social_media import SocialMediaTypes, SocialMediaActions
from social_media.webdriver import Agent
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request


class TestOkCollectors(TestCase):
    credential: SmCredential

    @classmethod
    def setUpTestData(cls):
        cls.credential = SmCredential.objects.create(
            user_name=settings.TEST_OK_LOGIN,
            password=settings.TEST_OK_PASSWORD,
            social_media=SocialMediaTypes.OK
        )

    @staticmethod
    def build_ok_options():
        inst = OkOptions()
        inst.post_count_limit = 45
        inst.discover_profiles_limit = 500
        return inst

    async def test_login(self):
        request = Request([SocialMediaActions.LOGIN], credentials=self.credential)
        run_agent = Agent(request)
        await run_agent.run()

        await self.credential.arefresh_from_db()
        self.assertIsNotNone(self.credential.session)
        pprint(self.credential.session)


    async def test_group_collector(self):
        suspect_group = await SuspectGroup.objects.acreate(
            url='https://ok.ru/radiorussia1',
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
        request.options = self.build_ok_options()

        run_agent = Agent(request)
        await run_agent.run()
        group: SmGroup = await SmGroup.objects.aget(suspect_group=suspect_group)
        pprint(group.__dict__)
        self.assertIsNotNone(group)
        self.assertEquals(group.oid, '54523677844453')
        self.assertEquals(group.name, 'Радио России')
        self.assertEquals(group.permalink, 'https://ok.ru/group/54523677844453')
        self.assertEquals(group.social_media, SocialMediaTypes.OK)


    async def test_profile_collector(self):
        suspect = await Suspect.objects.acreate(name='test')
        suspect_account = await SuspectSocialMediaAccount.objects.acreate(
            suspect=suspect,
            credentials=self.credential,
            link='https://ok.ru/profile/549710251260'
        )

        request = Request(
            actions=[
                SocialMediaActions.LOGIN,
                SocialMediaActions.PROFILE,
                SocialMediaActions.POSTS
            ],
            credentials=self.credential,
            suspect_identity=suspect_account
        )
        request.options = self.build_ok_options()

        run_agent = Agent(request)
        await run_agent.run()

    async def test_profile_discovery_collector(self):
        country = await Country.objects.acreate(
            name='Украина',
            code='ua'
        )
        suspect_place = await SuspectPlace.objects.acreate(
            city='Киев',
            country=country
        )

        request = Request(
            actions=[
                SocialMediaActions.LOGIN,
                SocialMediaActions.PROFILES_DISCOVERY
            ],
            credentials=self.credential,
            suspect_identity=suspect_place
        )
        request.options = self.build_ok_options()

        run_agent = Agent(request)
        await run_agent.run()



