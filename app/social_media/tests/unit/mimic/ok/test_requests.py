from pathlib import Path
from typing import Optional

from django.conf import settings
from django.test import SimpleTestCase

from social_media.dtos.oksessiondto import OkSessionDto
from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.device import default_device
from social_media.mimic.ok.flows.okgroupflow import OkGroupFlow
from social_media.mimic.ok.flows.okloginflow import OkLoginFlow
from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.auth.login import LoginResponseBody
from social_media.mimic.ok.requests.group.getinfo import GroupInfoItem


class OkRequestsTestCase(SimpleTestCase):
    async def login_or_restore_session(self, client: OkHttpClient):
        """
        Do a full login procedure or restore session from file
        @param client:
        @return:
        """

        path = Path(settings.MEDIA_ROOT) / 'ok_test_session.json'

        login_flow = OkLoginFlow(client)
        previous_session_dto: Optional[OkSessionDto] = None

        def serialize_session(session_dto: OkSessionDto):
            session_dto.cookie_jar = client.jar.to_base64()
            self.assertTrue(session_dto.cookie_jar, 'Cookie jar must be present')
            path.write_text(session_dto.to_json())

        if path.exists():
            session_dto_json = path.read_text()
            previous_session_dto: OkSessionDto = OkSessionDto.from_json(session_dto_json)

        response_body = await login_flow.login(settings.TEST_OK_LOGIN, settings.TEST_OK_PASSWORD, previous_session_dto)
        self.assertIsInstance(response_body, LoginResponseBody)
        self.assertTrue(response_body.session_key, 'Session key must be present')
        self.assertTrue(response_body.auth_token, 'Auth token must be present')

        serialize_session(response_body.to_session_dto())

    async def test_ok_processes(self):
        """
        Test OK processes like login, finding groups uuids, reading group info, posts, like, etc.

        It's a single test because we need to keep session key, cookies and overall state of the client as well as
        general request - response flow
        @return:
        """
        client = OkHttpClient(default_device)

        await self.login_or_restore_session(client)

        group_flow = OkGroupFlow(client)
        group_uuid = await group_flow.resolve_group_uid('https://ok.ru/demokratic')
        print(group_uuid)
        self.assertTrue(group_uuid)
        group_info = await group_flow.fetch_group_info(group_uuid)
        self.assertIsInstance(group_info, GroupInfoItem)

        stream_flow = OkStreamFlow(client)
        previous_anchor = None
        for page in range(1, 2):
            group_posts_response = await stream_flow.fetch_feed(group_uuid, previous_anchor)
            group_posts_body = group_posts_response.get_body()
            previous_anchor = group_posts_body.anchor

            for feed_item in group_posts_body.feeds:
                print(feed_item)
                media_topic = group_posts_body.find_media_topic(feed_item)
                likes_response = await stream_flow.fetch_likes(media_topic.like_summary.like_id)
                print(likes_response.get_body())
