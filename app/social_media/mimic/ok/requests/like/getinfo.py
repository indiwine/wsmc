import dataclasses
from copy import copy
from typing import Optional, List, Type, Union


from social_media.dtos import AuthorDto, SmProfileDto
from social_media.mimic.ok.requests.abstractrequest import GenericRequest, AbstractRequestParams, GenericResponseBody, \
    GenericResponse, RESPONSE_BODY, AbstractResponse
from social_media.common import nested_dataclass, dataclass_asdict_skip_none
from social_media.mimic.ok.requests.entities.user import UserItem


@dataclasses.dataclass
class LikeGetInfoParams(AbstractRequestParams):
    like_id: str
    count: int = 20
    fields: str = 'like.reacted_users,user.show_lock,user.can_vmail,user.last_name,user.pic190x190,user.gender,user.online,user.first_name,user.premium,user.vip,user.birthday,user.location,user.location_of_birth,user.url_profile,user.ref'
    anchor: Optional[str] = None

    def to_execute_dict(self) -> dict:
        return dataclass_asdict_skip_none(self)


@nested_dataclass
class ReactedUserItem:
    reaction: str
    date_ms: int
    user: Optional[UserItem] = None


class LikeGetInfoResponseBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.has_more: bool = False
        self.totalCount: int = 0
        self.reacted_users: List[ReactedUserItem] = []
        self.anchor: Optional[str] = None
        super().__init__(raw_params)


    def to_author_dtos(self) -> List[AuthorDto]:
        result = []
        for reacted_user in self.reacted_users:
            if reacted_user.user is not None:
                result.append(reacted_user.user.to_author_dto())
        return result

    def to_profile_dtos(self) -> List[SmProfileDto]:
        result = []
        for reacted_user in self.reacted_users:
            if reacted_user.user is not None:
                result.append(reacted_user.user.to_profile_dto())
        return result


class LikeGetInfoResponse(GenericResponse[LikeGetInfoResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return LikeGetInfoResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        response = copy(raw_response)
        response['reacted_users'] = [ReactedUserItem(**user) for user in response['reacted_users']]
        super().set_from_raw(response)


class LikeGetInfoRequest(GenericRequest[LikeGetInfoParams, None]):
    def __init__(self, like_id: str, previous_anchor: Optional[str] = None):
        params = LikeGetInfoParams(like_id, anchor=previous_anchor)

        super().__init__('like', 'getInfo', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LikeGetInfoResponse
