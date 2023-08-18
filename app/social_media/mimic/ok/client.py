import dataclasses
from typing import Optional
from django.conf import settings

import aiohttp
from aiohttp import ClientResponse, ClientSession

from social_media.mimic.ok.exceptions import OkApiCallException
from social_media.mimic.ok.requests.abstractrequest import AbstractRequest, OkRequestHttpMethod, AbstractResponse, \
    AbstractCustomPayloadEncoderMixin

BASE_URL = 'https://api.ok.ru/api/'


@dataclasses.dataclass
class OkHttpClientAuthOptions:
    application_key: str = settings.MIMIC_OK_APP_KEY
    session_key: Optional[str] = None
    screen: Optional[str] = None


class OkHttpClient:
    def __init__(self, auth_options: OkHttpClientAuthOptions = OkHttpClientAuthOptions(), ua: str = settings.MIMIC_OK_UA):
        self.auth_options = auth_options
        self.ua = ua

    def _build_session(self) -> ClientSession:
        return aiohttp.ClientSession(headers={
            'user-agent': self.ua
        })

    async def make(self, request: AbstractRequest) -> AbstractResponse:
        url = f'{BASE_URL}{request.pathed_method_name}'
        async with self._build_session() as session:
            payload = self.get_payload(request)
            payload.update(self.get_app_keys())

            if request.http_method == OkRequestHttpMethod.GET:
                async with session.get(url, params=payload) as response:
                    return await self.build_response(request, response)
            elif request.http_method == OkRequestHttpMethod.POST:
                post_params = {}
                headers = {}

                if isinstance(request, AbstractCustomPayloadEncoderMixin):
                    payload = request.encode(payload)
                    headers['content-type'] = request.get_content_type()
                    if request.get_content_encoding():
                        headers['Content-Encoding'] = request.get_content_encoding()

                    post_params['data'] = payload
                else:
                    param_key = 'json' if request.is_json() else 'data'
                    post_params[param_key] = payload

                async with session.post(url, headers=headers, **post_params) as response:
                    response_text = await response.text()
                    print(f'POST {url}:', response_text)
                    return await self.build_response(request, response)
            else:
                raise RuntimeError(f'Unknown Http request method: {request.http_method}')

    async def build_response(self, request: AbstractRequest, response_obj: ClientResponse) -> AbstractResponse:
        raw_response = await response_obj.json()
        self._throw_if_error(raw_response)
        response = request.bound_response_cls()(request)
        response.set_from_raw(raw_response)
        return response

    def get_payload(self, request: AbstractRequest) -> dict:
        return request.to_execute_dict()


    def set_session_key(self, session_key: str):
        self.auth_options.session_key = session_key

    def set_screen(self, screen: str):
        self.auth_options.screen = screen

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
