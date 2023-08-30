from pprint import pprint

from django.conf import settings
from django.test import TestCase

from social_media.models import SmCredential, SuspectGroup, SmGroup
from social_media.social_media import SocialMediaTypes, SocialMediaEntities
from social_media.webdriver import Agent
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

    async def test_login(self):
        request = Request([SocialMediaEntities.LOGIN], credentials=self.credential)
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
            entities=[
                SocialMediaEntities.LOGIN,
                SocialMediaEntities.GROUP,
                SocialMediaEntities.POSTS
            ],
            credentials=self.credential,
            suspect_identity=suspect_group
        )

        run_agent = Agent(request)
        await run_agent.run()
        group: SmGroup = await SmGroup.objects.aget(suspect_group=suspect_group)
        pprint(group.__dict__)
        self.assertIsNotNone(group)
        self.assertEquals(group.oid, '54523677844453')
        self.assertEquals(group.name, 'Радио России')
        self.assertEquals(group.permalink, 'https://ok.ru/group/54523677844453')
        self.assertEquals(group.social_media, SocialMediaTypes.OK)

