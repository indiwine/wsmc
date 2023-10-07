from dataclasses import dataclass
from typing import Optional, List, Union

from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericResponseBody, GenericResponse, \
    GenericRequest
from social_media.mimic.ok.requests.entities.user import UserItem


@dataclass
class UsersGetInfoParams(AbstractRequestParams):
    uids: Optional[str] = None
    fields: Optional[str] = 'first_name,last_name,url_profile'
    emptyPictures: Optional[bool] = None

class UsersGetInfoResponseBody(GenericResponseBody):
    def __init__(self, raw_params):
        self.users: List[UserItem] = raw_params
        super().__init__(raw_params)


class UsersGetInfoResponse(GenericResponse[UsersGetInfoResponseBody]):
    def set_from_raw(self, raw_response: Union[dict, list]):
        response = raw_response
        response['users'] = [UserItem(**user) for user in response['users']]
        super().set_from_raw(response)

    @staticmethod
    def get_body_class():
        return UsersGetInfoResponseBody


class UsersGetInfoRequest(GenericRequest[UsersGetInfoParams, None]):
    def __init__(self, uids: Optional[str] = None, supply_params: Optional[UsersGetInfoParams] = None):
        assert uids or supply_params, 'Either uids or supply_params must be provided'

        super().__init__('users', 'getInfo', UsersGetInfoParams(uids), supply_params=supply_params)

    @staticmethod
    def bound_response_cls():
        return UsersGetInfoResponse
