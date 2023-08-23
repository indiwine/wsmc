import asyncio
import random
from pathlib import Path
from pprint import pprint

from django.test import SimpleTestCase
from django.conf import settings

from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.device import default_device
from social_media.mimic.ok.log_requests.mocking import LogRequestMockTask, LogRequestMockPipeline
from social_media.mimic.ok.requests.auth.anonymlogin import AnonymLoginRequest, AnonymLoginResponse, \
    AnonymLoginResponseBody
from social_media.mimic.ok.requests.auth.login import LoginRequest
from social_media.mimic.ok.requests.executev2request import ExecuteV2Request


class OkRequestsTestCase(SimpleTestCase):
    async def test_auth_login(self):
        file_name = 'before_login_requests.xml'
        file_path = Path(__file__).parent / file_name
        before_login_tasks = LogRequestMockTask(file_path=str(file_path))
        before_login_tasks = LogRequestMockPipeline.execute_task(before_login_tasks)

        client = OkHttpClient(default_device)

        anon_login_request = AnonymLoginRequest()
        response = await client.make(anon_login_request)
        response_body: AnonymLoginResponseBody = response.get_body()
        client.set_session_key(response_body.session_key)
        for request in before_login_tasks.log_requests:
            random_int = random.randint(1, 10)
            print(f'Sleeping for {random_int} seconds')
            await asyncio.sleep(random_int)
            await client.make(request)


        batch_request = ExecuteV2Request('auth.login')
        batch_request.append(LoginRequest(settings.TEST_OK_LOGIN, settings.TEST_OK_PASSWORD))

        client.auth_options.screen = 'feed_main,profile_self'

        response = await client.make(batch_request)
        pprint(response)

    def test_login_by_token(self):
        pass


    def test_login_request(self):
        batch_request = ExecuteV2Request('auth.login')
        batch_request.append(LoginRequest(settings.TEST_OK_LOGIN, settings.TEST_OK_PASSWORD))
        pprint(batch_request.to_execute_dict())
