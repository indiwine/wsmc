from typing import Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.stream.entities.feedlikesummary import FeedLikeSummary
from social_media.mimic.ok.requests.stream.entities.feedresharesummary import FeedReShareSummary


@nested_dataclass
class FeedMediaTopic(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return None

    media: list
    id: str
    created_ms: int
    discussion_summary: dict
    like_summary: FeedLikeSummary
    reshare_summary: FeedReShareSummary
    author_ref: str
    owner_ref: str
    has_more: bool
    is_product: bool
    on_moderation: bool
    has_extended_stats: bool
    is_feeling: bool
    app_ref: Optional[str] = None
    capabilities: Optional[str] = None
    is_commenting_denied: Optional[bool] = None
