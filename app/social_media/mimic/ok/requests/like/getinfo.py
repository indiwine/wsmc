import dataclasses
from typing import Optional, List, Type

from social_media.mimic.ok.requests.abstractrequest import GenericRequest, AbstractRequestParams, GenericResponseBody, \
    GenericResponse, RESPONSE_BODY, AbstractResponse


@dataclasses.dataclass
class LikeGetInfoParams(AbstractRequestParams):
    like_id: str
    count: int = 20
    fields: str = 'like.reacted_users,user.show_lock,user.can_vmail,user.last_name,user.pic190x190,user.gender,user.online,user.first_name,user.premium,user.vip,user.birthday'
    anchor: Optional[str] = None


    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)

class UserItem:
    uid: str
    birthday: str
    birthdaySet: bool
    first_name: str
    last_name: str
    gender: str
    pic190x190: str
    pic_base: str
    can_vmail: bool
    premium: bool
    show_lock: bool

class ReactedUserItem:
    reaction: str
    date_ms: int
    user: UserItem

class LikeGetInfoResponseBody(GenericResponseBody):
    has_more: bool
    totalCount: int
    reacted_users: List[ReactedUserItem]
    anchor: Optional[str] = None

class LikeGetInfoResponse(GenericResponse):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return LikeGetInfoResponseBody

class LikeGetInfoRequest(GenericRequest):
    def __init__(self, group_id: str):
        params = LikeGetInfoParams(group_id)

        super().__init__('like', 'getInfo', params)


    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LikeGetInfoResponse

