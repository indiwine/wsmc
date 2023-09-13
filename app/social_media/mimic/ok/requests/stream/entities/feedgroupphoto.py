from typing import Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.stream.entities.feedlikesummary import FeedLikeSummary
from social_media.mimic.ok.requests.stream.entities.feedresharesummary import FeedReShareSummary


@nested_dataclass
class FeedGroupPhoto(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return None

    type: str
    id: str
    created_ms: int
    album_id: str
    standard_width: int
    standard_height: int
    pic_base: str
    discussion_summary: dict
    send_as_gift_available: bool
    text_detected: bool
    group_id: str
    preview: Optional[str] = None
    like_summary: Optional[FeedLikeSummary] = None
    reshare_summary: Optional[FeedReShareSummary] = None
    user_id: Optional[str] = None
    topic_id: Optional[str] = None
    picmp4: Optional = None
    attrs: Optional = None
