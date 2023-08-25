import asyncio
import random
from pathlib import Path
from typing import List, Optional

from django.conf import settings
from django.test import SimpleTestCase

from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.device import default_device
from social_media.mimic.ok.log_requests.mocking import LogRequestMockTask, LogRequestMockPipeline
from social_media.mimic.ok.requests.abstractrequest import AbstractRequest, AbstractResponse
from social_media.mimic.ok.requests.auth.anonymlogin import AnonymLoginRequest, AnonymLoginResponseBody
from social_media.mimic.ok.requests.auth.login import LoginRequest, LoginResponseBody, LoginResponse
from social_media.mimic.ok.requests.executev2request import ExecuteV2Request, ExecuteV2Response
from social_media.mimic.ok.requests.group.getinfo import GroupGetInfoResponse, GroupGetInfoRequest
from social_media.mimic.ok.requests.like.getinfo import LikeGetInfoRequest, LikeGetInfoResponse
from social_media.mimic.ok.requests.log.externallog import ExternalLogRequest
from social_media.mimic.ok.requests.stream.get import StreamGetRequest, StreamGetResponse, StreamGetResponseBody
from social_media.mimic.ok.requests.url.getinfo import UrlGetInfoRequest, UrlGetInfoBody, UrlGetInfoResponse


class OkRequestsTestCase(SimpleTestCase):
    @staticmethod
    async def create_and_run_batch_request(client: OkHttpClient,
                                           id: str,
                                           request: AbstractRequest) -> AbstractResponse:
        """
        Create batch request with single request and run it
        @param client:
        @param id:
        @param request:
        @return:
        """
        batch_request = ExecuteV2Request(id)
        batch_request.append(request)
        response: ExecuteV2Response = await client.make(batch_request)
        return response.find_response_by_request(request)

    def load_before_login_requests(self) -> List[ExternalLogRequest]:
        """
        Load requests from before login requests file
        @return:
        """

        file_name = 'before_login_requests.xml'
        file_path = Path(__file__).parent / file_name

        before_login_tasks = LogRequestMockTask(file_path=str(file_path))
        before_login_tasks = LogRequestMockPipeline.execute_task(before_login_tasks)
        return before_login_tasks.log_requests

    async def login_procedure(self, client: OkHttpClient) -> LoginResponseBody:
        """
        Login procedure simulation for OK
        @param client:
        @return: Login response body which can be used
        """

        # First we need to log in anonymously to get session key
        anon_login_request = AnonymLoginRequest()
        anon_login_response = await client.make(anon_login_request)
        response_body: AnonymLoginResponseBody = anon_login_response.get_body()

        # Set session key for client
        client.set_session_key(response_body.session_key)

        # Now we need to simulate log requests before login
        for log_request in self.load_before_login_requests():
            # A little bit of a delay to simulate real user
            random_int = random.randint(1, 10)
            await asyncio.sleep(random_int)

            await client.make(log_request)

        # Now let's prepare batch request with login request
        login_request = LoginRequest(settings.TEST_OK_LOGIN, settings.TEST_OK_PASSWORD)
        client.auth_options.screen = 'feed_main,profile_self'

        loging_response: LoginResponse = await self.create_and_run_batch_request(client, 'auth.login', login_request)
        login_response_body: LoginResponseBody = loging_response.get_body()

        self.assertTrue(login_response_body.session_key, 'Session key must be present')

        # Once we received a real session key, we need to set it to client
        client.set_session_key(login_response_body.session_key)

        return login_response_body

    async def fetch_group_uuid(self, client: OkHttpClient) -> UrlGetInfoBody:
        url = 'https://ok.ru/alexnews.r'

        url_info_request = UrlGetInfoRequest(url)
        url_info_response: UrlGetInfoResponse = await self.create_and_run_batch_request(client,
                                                                                        'stream.get-first',
                                                                                        url_info_request)
        self.assertIsInstance(url_info_response, UrlGetInfoResponse)
        return url_info_response.get_body()

    async def fetch_group_info(self, client: OkHttpClient, group_uuid: str):
        group_info_request = GroupGetInfoRequest(group_uuid)
        group_info_response: GroupGetInfoResponse = await self.create_and_run_batch_request(client,
                                                                                            'group.getInfo',
                                                                                            group_info_request)

        self.assertIsInstance(group_info_response, GroupGetInfoResponse)
        return group_info_response.find_group_info(group_uuid)

    async def fetch_group_posts(
        self,
        client: OkHttpClient,
        group_uuid: str,
        previous_anchor: Optional[str] = None
    ) -> StreamGetResponse:
        batch_id = 'stream.get-first' if not previous_anchor else 'stream.get-more'

        stream_get_request = StreamGetRequest(group_uuid)
        stream_get_response: StreamGetResponse = await self.create_and_run_batch_request(client,
                                                                                         batch_id,
                                                                                         stream_get_request)

        self.assertIsInstance(stream_get_response, StreamGetResponse)
        return stream_get_response

    async def fetch_post_likes(self, client: OkHttpClient, like_id: str) -> LikeGetInfoResponse:
        batch_id = 'like.getInfo'
        like_info_request = LikeGetInfoRequest(like_id)
        like_info_response: LikeGetInfoResponse = await self.create_and_run_batch_request(client,
                                                                                          batch_id,
                                                                                          like_info_request)
        self.assertIsInstance(like_info_response, LikeGetInfoResponse)
        return like_info_response

    async def test_ok_processes(self):
        """
        Test OK processes like login, finding groups uuids, reading group info, posts, like, etc.

        It's a single test because we need to keep session key, cookies and overall state of the client as well as
        general request - response flow
        @return:
        """
        client = OkHttpClient(default_device)

        login_response = await self.login_procedure(client)
        group_url_info = await self.fetch_group_uuid(client)
        group_uuid = group_url_info.objectIdEncoded
        self.assertTrue(group_uuid)
        group_info = await self.fetch_group_info(client, group_uuid)

        for page in range(1, 2):
            group_posts_response = await self.fetch_group_posts(client, group_uuid)
            group_posts_body = group_posts_response.get_body()
            for feed_item in group_posts_body.feeds:
                print(feed_item)
                media_topic = group_posts_body.find_media_topic(feed_item)
                likes_response = await self.fetch_post_likes(client, media_topic.like_summary.like_id)
