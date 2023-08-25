import dataclasses
from typing import Type, Union, Optional

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
    def __init__(self, raw_params: Union[dict, list]):
        self.uid: Optional[str] = None
        self.session_key: Optional[str] = None
        self.session_secret_key: Optional[str] = None
        self.auth_token: Optional[str] = None
        self.api_server: Optional[str] = None
        self.auth_sig: Optional[str] = None
        self.activated_profile: Optional[bool] = None
        self.auth_hash: Optional[str] = None
        super().__init__(raw_params)


class LoginResponse(GenericResponse[LoginResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return LoginResponseBody


class LoginRequest(GenericRequest[LoginParams]):
    def __init__(self, user_name: str, password: str):
        params = LoginParams(user_name, password)

        super().__init__('auth', 'login', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LoginResponse
