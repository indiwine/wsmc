import json
from typing import Type, Optional, Union

from ..abstractrequest import GenericRequest, AbstractRequestParams, OkRequestHttpMethod, GenericResponseBody, \
    GenericResponse, RESPONSE_BODY, AbstractResponse


class AnonymLoginParams(AbstractRequestParams):
    gaid: str = 'unknown'
    session_data: dict = {
        'device_id': 'unknown',
        'version': 2,
        'client_version': 'android_8',
        'client_type': 'SDK_ANDROID'
    }

    def configure_before_send(self, device, auth_options):
        self.gaid = device.gaid
        self.session_data['device_id'] = device.get_device_id()

    def to_execute_dict(self) -> dict:
        return {
            'gaid': self.gaid,
            'session_data': json.dumps(self.session_data)
        }


class AnonymLoginResponseBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.session_key: Optional[str] = None
        self.session_secret_key: Optional[str] = None
        self.api_server: Optional[str] = None
        self.activated_profile: Optional[str] = None
        super().__init__(raw_params)


class AnonymLoginResponse(GenericResponse[AnonymLoginResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return AnonymLoginResponseBody


class AnonymLoginRequest(GenericRequest):

    @property
    def http_method(self) -> OkRequestHttpMethod:
        return OkRequestHttpMethod.GET

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return AnonymLoginResponse

    def __init__(self):
        super().__init__('auth', 'anonymLogin', AnonymLoginParams())
