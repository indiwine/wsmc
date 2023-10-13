import dataclasses
from typing import List, Union, Type, Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, GenericResponseBody, \
    GenericResponse, AbstractResponse


@dataclasses.dataclass
class UsersGetRelationInfoParams(AbstractRequestParams):
    fields: Optional[str] = None
    friend_ids: Optional[str] = None


@nested_dataclass
class UserRelationItem:
    uid: str
    friend: bool
    friend_invitation: bool
    invited_by_friend: bool
    blocks: bool
    blocked: bool
    capabilities: str
    feed_subscription: bool


class UsersGetRelationInfoResponseBody(GenericResponseBody):
    relations: List[UserRelationItem]


class UsersGetRelationInfoResponse(GenericResponse[UsersGetRelationInfoResponseBody]):
    @staticmethod
    def get_body_class():
        return UsersGetRelationInfoResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        response = raw_response.copy()
        response['relations'] = [UserRelationItem(**relation) for relation in response['relations']]
        super().set_from_raw(response)


class UsersGetRelationInfoRequest(GenericRequest[UsersGetRelationInfoParams, None]):
    def __init__(self, params: Optional[UsersGetRelationInfoParams] = None, supply_params: Optional[UsersGetRelationInfoParams] = None):
        assert params or supply_params, 'Either params or supply_params must be provided'
        super().__init__(
            'users',
            'getRelationInfo',
            params=params,
            supply_params=supply_params
        )

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return UsersGetRelationInfoResponse
