from typing import Type

from ..abstractrequest import AbstractRequestParams, GenericRequest, GenericResponse, \
    GenericResponseBody, RESPONSE_BODY, AbstractResponse


class LoginParams(AbstractRequestParams):
    user_name: str
    password: str
    gen_token: bool = True
    verification_supported: bool = True
    verification_supported_v: str = "6"

    def to_execute_dict(self) -> dict:
        result = vars(self)
        result['deviceId'] = 'INSTALL_ID=a34865a3-021c-4f9b-aab7-6eac042e8884;ANDROID_ID=66de9c2ac05fd4f2;'
        result['gaid'] = '274b6ed2-4358-496e-a1ae-892e52242549'
        return result


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
        params = LoginParams()
        params.user_name = user_name
        params.password = password

        super().__init__('auth', 'login', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LoginResponse
