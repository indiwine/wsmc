import dataclasses
from typing import Optional

from social_media.dtos import AuthorDto
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity


@dataclasses.dataclass
class FeedUser(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return self.name

    uid: str
    birthday: str
    birthdaySet: bool
    first_name: str
    last_name: str
    name: str
    gender: str
    location: dict
    last_online_ms: int
    pic_full: str
    pic_base: str
    premium: bool
    show_lock: bool
    common_friends_count: int
    executor: bool
    age: Optional[int] = None

    def to_author_dto(self) -> AuthorDto:
        """
        Convert to AuthorDto
        @return:
        """
        return AuthorDto(
            self.uid,
            self.name,
            f'https://ok.ru/profile/{self.uid}',
            is_group=False
        )
