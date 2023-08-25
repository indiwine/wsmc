import dataclasses
from typing import Type

from .login import LoginResponse
from ..abstractrequest import GenericRequest, AbstractRequestParams, AbstractResponse


@dataclasses.dataclass
class LoginByTokenParams(AbstractRequestParams):
    token: str
    away: bool = True
    verification_supported: bool = True
    verification_supported_v: str = "6"
    deviceId: str = 'unknown'
    gaid: str = 'unknown'

    def configure_before_send(self, device, auth_options):
        self.deviceId = device.get_device_id()
        self.gaid = device.gaid

    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)

class LoginByTokenRequest(GenericRequest[LoginByTokenParams]):
    def __init__(self, auth_token: str):
        params = LoginByTokenParams(auth_token)
        super().__init__('auth', 'loginByToken', params)

    def is_json(self) -> bool:
        return False

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LoginResponse

