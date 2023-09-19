import dataclasses
from typing import Optional

from social_media.dtos import AuthorDto
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity


@dataclasses.dataclass
class FeedGroup(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return self.name

    uid: str
    name: str
    created_ms: int
    photo_id: str
    main_photo: dict
    premium: bool
    private: bool
    paid_access: str
    category: str
    revenue_pp_enabled: bool
    pin_notifications_off: bool
    attrs: Optional[dict] = None

    def to_author_dto(self) -> AuthorDto:
        """
        Convert to AuthorDto
        @return:
        """
        return AuthorDto(
            self.uid,
            self.name,
            f'https://ok.ru/group/{self.uid}',
            is_group=True
        )
