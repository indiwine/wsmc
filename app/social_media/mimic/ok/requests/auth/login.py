import dataclasses
from typing import Type

from ..abstractrequest import AbstractRequestParams, GenericRequest, GenericResponse, \
    GenericResponseBody, RESPONSE_BODY, AbstractResponse


@dataclasses.dataclass
class LoginParams(AbstractRequestParams):
    user_name: str
    password: str
    gen_token: bool = True
    verification_supported: bool = True
    verification_supported_v: str = "6"
    deviceId: str = 'unknown'
    gaid: str = 'unknown'

    def configure_before_send(self, device, auth_options):
        self.deviceId = device.get_device_id()
        self.gaid = device.gaid

    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)


class LoginResponseBody(GenericResponseBody):
    uid: str
    session_key: str
    session_secret_key: str
    auth_token: str
    api_server: str
    auth_sig: str
    activated_profile: bool
    auth_hash: str


class LoginResponse(GenericResponse):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return LoginResponseBody


class LoginRequest(GenericRequest):
    def __init__(self, user_name: str, password: str):
        params = LoginParams(user_name, password)

        super().__init__('auth', 'login', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LoginResponse
