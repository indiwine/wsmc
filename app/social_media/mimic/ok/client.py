import base64
import dataclasses
import pickle

import aiohttp
from aiohttp import ClientResponse, ClientSession

from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.exceptions import OkApiCallException
from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.requests.abstractrequest import AbstractRequest, OkRequestHttpMethod, AbstractResponse, \
    AbstractCustomPayloadEncoderMixin

BASE_URL = 'https://api.ok.ru/api/'

class SerializableCookieJar(aiohttp.CookieJar):
    def to_base64(self) -> str:
        binary_data = pickle.dumps(self._cookies, protocol=pickle.HIGHEST_PROTOCOL)

        # Convert binary_data to base64 string
        return base64.b64encode(binary_data).decode('utf-8')

    def from_base64(self, base64_str: str):
        binary_data = base64.b64decode(base64_str)
        self._cookies = pickle.loads(binary_data)
class OkHttpClient:
    def __init__(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions = OkHttpClientAuthOptions()):
        self.auth_options = auth_options
        self.device = device
        self.jar = SerializableCookieJar()

    def _build_session(self) -> ClientSession:
        return aiohttp.ClientSession(headers={
            'user-agent': self.device.get_user_agent()
        }, cookie_jar=self.jar)

    async def make(self, request: AbstractRequest) -> AbstractResponse:
        url = f'{BASE_URL}{request.pathed_method_name}'
        async with self._build_session() as session:
            # Configure request params
            request.configure(self.device, self.auth_options)

            # Build payload
            payload = self.get_payload(request)
            # Inject required app keys and tokens
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
