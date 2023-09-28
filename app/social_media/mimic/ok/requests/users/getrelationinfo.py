import dataclasses
from typing import List, Union, Type

from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, GenericResponseBody, \
    GenericResponse, AbstractResponse


@dataclasses.dataclass
class UsersGetRelationInfoParams(AbstractRequestParams):
    fields: str = '*'


@dataclasses.dataclass
class UsersGetRelationInfoSupplyParams(AbstractRequestParams):
    friend_ids: str = "search.global.user_ids"


@dataclasses.dataclass
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


class UsersGetRelationInfoRequest(GenericRequest[UsersGetRelationInfoParams, UsersGetRelationInfoSupplyParams]):
    def __init__(self):
        super().__init__(
            'users',
            'getRelationInfo',
            params=UsersGetRelationInfoParams(),
            supply_params=UsersGetRelationInfoSupplyParams()
        )

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return UsersGetRelationInfoResponse
