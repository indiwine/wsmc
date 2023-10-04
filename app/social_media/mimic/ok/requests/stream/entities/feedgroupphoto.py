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
    standard_width: Optional[int] = None
    standard_height: Optional[int] = None
    pic_base: Optional[str] = None
    discussion_summary: Optional[dict] = None
    send_as_gift_available: Optional[bool] = None
    text_detected: Optional[bool] = None
    group_id: Optional[str] = None
    preview: Optional[str] = None
    like_summary: Optional[FeedLikeSummary] = None
    reshare_summary: Optional[FeedReShareSummary] = None
    user_id: Optional[str] = None
    topic_id: Optional[str] = None
    picmp4: Optional = None
    attrs: Optional = None
    sensitive: Optional = None
