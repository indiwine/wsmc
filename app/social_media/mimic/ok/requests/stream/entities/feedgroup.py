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
    created_ms: Optional[int] = None
    photo_id: Optional[str] = None
    main_photo: Optional[dict] = None
    premium: Optional[bool] = None
    private: Optional[bool] = None
    paid_access: Optional[str] = None
    category: Optional[str] = None
    revenue_pp_enabled: Optional[bool] = None
    pin_notifications_off: Optional[bool] = None
    attrs: Optional[dict] = None
    member_status: Optional[str] = None

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
