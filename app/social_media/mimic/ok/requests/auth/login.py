import dataclasses
from typing import Type
from django.conf import settings

from ..abstractrequest import AbstractRequestParams, GenericRequest, GenericResponse, \
    GenericResponseBody, RESPONSE_BODY, AbstractResponse
from ..common import append_gaid_and_device_id


@dataclasses.dataclass
class LoginParams(AbstractRequestParams):
    user_name: str
    password: str
    gen_token: bool = True
    verification_supported: bool = True
    verification_supported_v: str = "6"

    def to_execute_dict(self) -> dict:
        result = dataclasses.asdict(self)
        return append_gaid_and_device_id(result)


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
