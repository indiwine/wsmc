import dataclasses
from typing import Type

from .login import LoginResponse
from ..abstractrequest import GenericRequest, AbstractRequestParams, AbstractResponse
from ..common import append_gaid_and_device_id


@dataclasses.dataclass
class LoginByTokenParams(AbstractRequestParams):
    token: str
    away: bool = True
    verification_supported: bool = True
    verification_supported_v: str = "6"
    def to_execute_dict(self) -> dict:
        result = dataclasses.asdict(self)
        return append_gaid_and_device_id(result)


class LoginByTokenRequest(GenericRequest):
    def __init__(self, token: str):
        params = LoginByTokenParams(token)
        super().__init__('auth', 'loginByToken', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LoginResponse

