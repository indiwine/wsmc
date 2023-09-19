import dataclasses
from copy import copy
from typing import Optional, List, Type, Union


from social_media.dtos import AuthorDto, SmProfileDto, SmProfileMetadata
from social_media.mimic.ok.requests.abstractrequest import GenericRequest, AbstractRequestParams, GenericResponseBody, \
    GenericResponse, RESPONSE_BODY, AbstractResponse
from social_media.mimic.ok.requests.common import dataclass_asdict_skip_none
from social_media.common import nested_dataclass
from social_media.webdriver.common import date_time_parse


@dataclasses.dataclass
class LikeGetInfoParams(AbstractRequestParams):
    like_id: str
    count: int = 20
    fields: str = 'like.reacted_users,user.show_lock,user.can_vmail,user.last_name,user.pic190x190,user.gender,user.online,user.first_name,user.premium,user.vip,user.birthday,user.location,user.location_of_birth,user.url_profile,user.ref'
    anchor: Optional[str] = None

    def to_execute_dict(self) -> dict:
        return dataclass_asdict_skip_none(self)


@dataclasses.dataclass
class UserLocation:
    city: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    countryName: Optional[str] = None

@nested_dataclass
class UserItem:
    uid: str
    birthday: str
    """
    Users birthday in format YYYY-MM-DD or MM-DD
    """
    birthdaySet: bool
    first_name: str
    last_name: str
    gender: str
    pic190x190: str
    can_vmail: bool
    premium: bool
    show_lock: bool
    pic_base: Optional[str] = None
    online: Optional[bool] = None
    location: Optional[UserLocation] = None
    location_of_birth: Optional[UserLocation] = None
    url_profile: Optional[str] = None
    ref: Optional[str] = None
    is_hobby_expert: Optional[bool] = None

    def to_author_dto(self) -> AuthorDto:
        return AuthorDto(
            oid=self.uid,
            name=f'{self.first_name} {self.last_name}',
            url=self.url_profile,
            is_group=False
        )

    def to_profile_dto(self) -> SmProfileDto:
        dto = SmProfileDto(
            oid=self.uid,
            name=f'{self.first_name} {self.last_name}'
        )

        if self.birthdaySet:
            dto.birthdate = date_time_parse(self.birthday, date_formats=['%Y-%m-%d', '%m-%d'])

        if self.location is not None:
            if self.location.city is not None:
                dto.location = self.location.city

            if self.location.country is not None:
                dto.country = self.location.country

        if self.location_of_birth is not None and self.location_of_birth.city is not None:
            dto.home_town = self.location_of_birth.city


        if self.url_profile is not None:
            dto.metadata = SmProfileMetadata(permalink=self.url_profile)

        return dto

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


class LikeGetInfoRequest(GenericRequest[LikeGetInfoParams]):
    def __init__(self, like_id: str, previous_anchor: Optional[str] = None):
        params = LikeGetInfoParams(like_id, anchor=previous_anchor)

        super().__init__('like', 'getInfo', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return LikeGetInfoResponse
