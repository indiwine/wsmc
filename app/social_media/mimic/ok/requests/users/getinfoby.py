import dataclasses
from copy import copy
from typing import Union, Type

from social_media.mimic.ok.requests.abstractrequest import GenericRequest, GenericResponse, AbstractRequestParams, \
    GenericResponseBody, AbstractResponse
from social_media.mimic.ok.requests.entities.user import UserItem


@dataclasses.dataclass
class UserGetInfoByParams(AbstractRequestParams):
    uid: str
    fields: str = 'uid,birthday,first_name,last_name,gender,pic190x190,can_vmail,premium,show_lock,pic_base,online,current_location,location,location_of_birth,url_profile,ref'
    register_as_guest: bool = False
    use_default_cover: bool = False


class UserGetInfoByResponseBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.user: UserItem = None
        super().__init__(raw_params)


class UserGetInfoByResponse(GenericResponse[UserGetInfoByResponseBody]):
    @staticmethod
    def get_body_class():
        return UserGetInfoByResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        response = copy(raw_response)
        response['user'] = UserItem(**response['user'])
        super().set_from_raw(response)


class UserGetInfoByRequest(GenericRequest[UserGetInfoByParams, None]):
    def __init__(self, uid: str):
        super().__init__('users', 'getInfoBy', UserGetInfoByParams(uid))

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return UserGetInfoByResponse
