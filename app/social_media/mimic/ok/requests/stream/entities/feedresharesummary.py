from typing import Optional

from social_media.common import nested_dataclass


@nested_dataclass
class FeedReShareSummary:
    count: int
    self: bool
    self_owner: bool
    reshare_like_id: str
    reshare_possible: bool
    reshare_available_for_chats: bool
    reshare_object_ref: str
    reshare_available_for_external: Optional[bool] = None
    reshare_external_link: Optional[str] = None
    last_reshare_date_ms: Optional[int] = None
