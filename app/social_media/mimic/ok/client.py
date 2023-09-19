import dataclasses
import logging
from typing import Optional

import aiohttp
from aiohttp import ClientResponse, ClientSession

from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.exceptions import OkApiCallException
from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.requests.abstractrequest import AbstractRequest, OkRequestHttpMethod, AbstractResponse, \
    AbstractCustomPayloadEncoderMixin
from social_media.mimic.ok.requests.auth.login import LoginResponseBody
from social_media.mimic.ok.serializablecookiejar import SerializableCookieJar

BASE_URL = 'https://api.ok.ru/api/'

logger = logging.getLogger(__name__)


class OkHttpClient:
    LOG_REQUESTS = False

    def __init__(self, device: AndroidDevice, auth_options: Optional[OkHttpClientAuthOptions] = None):
        logger.debug(f'Creating OkHttpClient with device: {device}')
        if auth_options is None:
            auth_options = OkHttpClientAuthOptions()

        self.auth_options = auth_options
        self.device = device
        self.jar = SerializableCookieJar()

    def _build_session(self) -> ClientSession:
        return aiohttp.ClientSession(headers={
            'user-agent': self.device.get_user_agent()
        }, cookie_jar=self.jar)

    async def make(self, request: AbstractRequest) -> AbstractResponse:
        url = f'{BASE_URL}{request.pathed_method_name}'
        if self.LOG_REQUESTS:
            logger.debug(f'Making request to {request}')

        async with self._build_session() as session:
            # Configure request params
            request.configure(self.device, self.auth_options)

            # Build payload
            payload = self.get_payload(request)
            # Inject required app keys and tokens
            payload.update(self.get_app_keys())
            if self.LOG_REQUESTS:
                logger.debug(f'Payload: {payload}')

            if request.http_method == OkRequestHttpMethod.GET:

                logger.info(f'GET {url}')
                async with session.get(url, params=payload) as response:
                    return await self.build_response(request, response)
            elif request.http_method == OkRequestHttpMethod.POST:
                logger.info(f'POST {url}')

                post_params = {}
                headers = {}

                if isinstance(request, AbstractCustomPayloadEncoderMixin):
                    # logger.debug(f'Using custom payload encoder for {request}')
                    payload = request.encode(payload)
                    headers['content-type'] = request.get_content_type()
                    if request.get_content_encoding():
                        headers['Content-Encoding'] = request.get_content_encoding()

                    post_params['data'] = payload
                else:
                    param_key = 'json' if request.is_json() else 'data'
                    # logger.debug(f'Using default payload encoder for {request}, with param key: {param_key}')
                    post_params[param_key] = payload

                async with session.post(url, headers=headers, **post_params) as response:
                    response_text = await response.text()
                    # logger.debug(f'Response text: {response_text}')
                    return await self.build_response(request, response)
            else:
                raise RuntimeError(f'Unknown Http request method: {request.http_method}')

    async def build_response(self, request: AbstractRequest, response_obj: ClientResponse) -> AbstractResponse:
        raw_response = await response_obj.json()
        self._throw_if_error(raw_response)
        response_cls = request.bound_response_cls()

        logger.debug(f'Building response for {request} with class {response_cls}')

        response = response_cls(request)
        response.set_from_raw(raw_response)
        return response

    def get_payload(self, request: AbstractRequest) -> dict:
        return request.to_execute_dict()

    def set_session_key(self, session_key: str):
        logger.debug(f'Setting session key: {session_key}')
        self.auth_options.session_key = session_key

    def set_screen(self, screen: str):
        logger.debug(f'Setting screen: {screen}')
        self.auth_options.screen = screen

    def set_current_login_data(self, login_data: LoginResponseBody):
        logger.debug(f'Setting current login data: {login_data}')
        self.auth_options.current_login_data = login_data

    @staticmethod
    def _throw_if_error(data):
        if isinstance(data, dict) \
            and 'error_msg' in data \
            and 'error_code' in data \
            and 'error_data' in data:
            raise OkApiCallException(
                data['error_code'],
                data['error_msg'],
                data['error_data']
            )

    def get_app_keys(self) -> dict:
        result = dataclasses.asdict(self.auth_options, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        if 'screen' in result:
            result['__screen'] = result['screen']
            del result['screen']

        return result
