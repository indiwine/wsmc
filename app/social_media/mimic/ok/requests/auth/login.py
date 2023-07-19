import dataclasses

from ..abstractrequest import AbstractRequestParams, GenericRequest


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


class LoginRequest(GenericRequest):
    def __init__(self, params: AbstractRequestParams):
        super().__init__('auth', 'login', params)



