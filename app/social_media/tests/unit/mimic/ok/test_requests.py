import asyncio
import json
from pathlib import Path
from pprint import pprint
from typing import Optional

from django.conf import settings
from django.test import SimpleTestCase

from social_media.dtos import SmPostDto, AuthorDto, SmProfileDto
from social_media.dtos.oksessiondto import OkSessionDto
from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.flows.okcommonflow import OkCommonFlow
from social_media.mimic.ok.flows.okloginflow import OkLoginFlow
from social_media.mimic.ok.flows.oksearchflow import OkSearchFlow
from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.auth.login import LoginResponseBody
from social_media.mimic.ok.requests.entities.user import UserItem
from social_media.mimic.ok.requests.group.getinfo import GroupInfoItem
from social_media.mimic.ok.requests.search.global_ import SearchGlobalResponseBody
from social_media.mimic.ok.requests.search.locationsforfilter import SearchedLocation
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.users.getinfo import UsersGetInfoResponseBody
from social_media.mimic.ok.requests.users.getrelationinfo import UsersGetRelationInfoResponseBody


class OkRequestsTestCase(SimpleTestCase):
    ok_http_client: OkHttpClient
    logged_in: bool

    @classmethod
    def setUpClass(cls):
        if not settings.TEST_OK_LOGIN or not settings.TEST_OK_PASSWORD:
            raise ValueError('OK login and password must be present')
        cls.ok_http_client = OkHttpClient()
        cls.logged_in = False

    async def login_or_restore_session(self, client: OkHttpClient):
        """
        Do a full login procedure or restore session from file
        @param client:
        @return:
        """
        if self.logged_in:
            return

        path = Path(settings.MEDIA_ROOT) / 'ok_test_session.json'

        login_flow = OkLoginFlow(client)
        previous_session_dto: Optional[OkSessionDto] = None

        def serialize_session(session_dto: OkSessionDto):
            session_dto.cookie_jar = client.jar.to_base64()
            session_dto.device = client.device
            self.assertTrue(session_dto.cookie_jar, 'Cookie jar must be present')
            self.assertTrue(session_dto.device, 'Device must be present')
            path.write_text(session_dto.to_json())

        if path.exists():
            session_dto_json = path.read_text()
            previous_session_dto: OkSessionDto = OkSessionDto.from_json(session_dto_json)

        response_body = await login_flow.login(settings.TEST_OK_LOGIN, settings.TEST_OK_PASSWORD, previous_session_dto)
        self.assertIsInstance(response_body, LoginResponseBody)
        self.assertTrue(response_body.session_key, 'Session key must be present')
        self.assertTrue(response_body.auth_token, 'Auth token must be present')

        serialize_session(response_body.to_session_dto())
        self.logged_in = True

    async def test_profile_info(self):
        await self.login_or_restore_session(self.ok_http_client)
        group_flow = OkCommonFlow(self.ok_http_client)
        user_id = await group_flow.resolve_url_to_uid('https://ok.ru/profile/549710251260')
        user_info = await group_flow.fetch_user_info(user_id)
        self.assertIsInstance(user_info, UserItem)
        pprint(user_info)
        stream_flow = OkStreamFlow(self.ok_http_client)
        posts = await stream_flow.fetch_feed(uid=user_id)
        for post_dto, target_entity in posts.get_body().post_generator():
            pprint(post_dto)
            await self.get_likes(target_entity, stream_flow)

    async def test_ok_processes(self):
        """
        Test OK processes like login, finding groups uuids, reading group info, posts, like, etc.

        It's a single test because we need to keep session key, cookies and overall state of the client as well as
        general request - response flow
        @return:
        """

        await self.login_or_restore_session(self.ok_http_client)
        group_flow = OkCommonFlow(self.ok_http_client)
        group_uuid = await group_flow.resolve_url_to_uid('https://ok.ru/group/70000000550380')

        self.assertTrue(group_uuid)
        group_info = await group_flow.fetch_group_info(group_uuid)
        self.assertIsInstance(group_info, GroupInfoItem)

        stream_flow = OkStreamFlow(self.ok_http_client)
        previous_anchor = None
        for page in range(1, 4):

            group_posts_response = await stream_flow.fetch_feed(group_uuid, previous_anchor=previous_anchor)
            group_posts_body = group_posts_response.get_body()

            save_file = Path(settings.MEDIA_ROOT) / f'ok_test_posts_{page}.json'
            save_file.write_text(json.dumps(group_posts_response.raw_body, indent=4, ensure_ascii=False))

            previous_anchor = group_posts_body.anchor

            for post_dto, target_entity in group_posts_body.post_generator():
                pprint(post_dto)
                self.assertIsInstance(post_dto, SmPostDto)
                self.assertIsInstance(target_entity, BaseFeedEntity)
                self.assertTrue(post_dto.sm_post_id)
                self.assertTrue(post_dto.social_media)
                self.assertTrue(post_dto.datetime)
                self.assertTrue(post_dto.author)
                if not post_dto.permalink:
                    print('No permalink, in post!')

                await self.get_likes(target_entity, stream_flow)

            await asyncio.sleep(10)

    async def test_search_locations(self):
        await self.login_or_restore_session(self.ok_http_client)
        search_flow = OkSearchFlow(self.ok_http_client)
        locations = await search_flow.search_locations_for_filter('Москва')

        for location in locations:
            self.assertIsInstance(location, SearchedLocation)
            self.assertTrue(location.text)
            self.assertTrue(location.city)
            self.assertTrue(location.country)
            self.assertTrue(location.city_id)
            self.assertTrue(location.countryId)
            self.assertTrue(location.position)
            pprint(location)

    async def test_search_users(self):
        await self.login_or_restore_session(self.ok_http_client)
        search_flow = OkSearchFlow(self.ok_http_client)
        locations = await search_flow.search_locations_for_filter('Киев, Украина')
        search_body, relations_body, users_body = await search_flow.search_users_by_location(locations[0])
        self.assertIsInstance(search_body, SearchGlobalResponseBody)
        self.assertIsInstance(relations_body, UsersGetRelationInfoResponseBody)
        self.assertIsInstance(users_body, UsersGetInfoResponseBody)
        self.assertTrue(search_body.anchor)
        for user in users_body.users:
            self.assertIsInstance(user, UserItem)
            dto = user.to_profile_dto()
            self.assertIsInstance(dto, SmProfileDto)

    async def get_likes(self, target_entity: BaseFeedEntity, stream_flow: OkStreamFlow):

        like_summary = target_entity.extract_like_summary()
        if like_summary is None:
            print('No like summary, skipping')
            return

        total_likes_count = like_summary.count
        if total_likes_count == 0:
            print('No likes, skipping')
            return

        like_id = like_summary.like_id

        previous_anchor = None
        while True:
            likes_response = await stream_flow.fetch_likes(like_id, previous_anchor)
            likes_body = likes_response.get_body()

            authors = likes_body.to_author_dtos()
            pprint(authors)
            self.assertIsInstance(authors, list)

            for author in authors:
                self.assertIsInstance(author, AuthorDto)
                self.assertTrue(author.oid)
                self.assertTrue(author.name)
                self.assertTrue(author.url)
                self.assertFalse(author.is_group)

            previous_anchor = likes_body.anchor
            if not likes_body.has_more:
                print('No more likes available, stopping')
                break
