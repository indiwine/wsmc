import dataclasses
from typing import Optional

from social_media.common import nested_dataclass
from social_media.dtos import AuthorDto, SmProfileDto, SmProfileMetadata
from social_media.webdriver.common import date_time_parse


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
    gender: Optional[str] = None
    pic190x190: Optional[str] = None
    can_vmail: Optional[bool] = None
    premium: Optional[bool] = None
    show_lock: Optional[bool] = None
    pic_base: Optional[str] = None
    online: Optional[bool] = None
    location: Optional[UserLocation] = None
    location_of_birth: Optional[UserLocation] = None
    url_profile: Optional[str] = None
    ref: Optional[str] = None
    is_hobby_expert: Optional[bool] = None
    last_online_ms: Optional[int] = None
    pic128x128: Optional[str] = None
    pic240min: Optional[str] = None
    pic320min: Optional[str] = None
    private: Optional = None
    age: Optional[int] = None

    @property
    def has_url(self):
        return self.url_profile is not None

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
