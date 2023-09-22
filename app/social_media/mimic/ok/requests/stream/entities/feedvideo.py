from typing import Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.stream.entities.feedlikesummary import FeedLikeSummary
from social_media.mimic.ok.requests.stream.entities.feedresharesummary import FeedReShareSummary


@nested_dataclass
class FeedVideo(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return self.title

    id: str
    permalink: str
    title: str
    content_presentations: list
    status: str
    from_time: int
    in_history: bool
    last_seen: int

    thumbnail_url: str
    small_thumbnail_url: str
    big_thumbnail_url: str

    base_thumbnail_url: str
    duration: int
    created_ms: int
    total_views: int

    author_ref: str
    owner_ref: str
    height: int
    width: int
    added_to_watch_later: bool
    m_subscribed: bool

    url_ultrahd: Optional[str] = None
    url_quadhd: Optional[str] = None
    cover_preview: Optional[str] = None
    discussion_summary: Optional[dict] = None
    like_summary: Optional[FeedLikeSummary] = None
    reshare_summary: Optional[FeedReShareSummary] = None
    description: Optional[str] = None
    url_high: Optional[str] = None
    url_fullhd: Optional[str] = None
    url_webm_dash: Optional[str] = None
    url_low: Optional[str] = None
    url_mobile: Optional[str] = None
    url_tiny: Optional[str] = None
    url_dash: Optional[str] = None
    url_hls: Optional[str] = None
    url_live_hls: Optional[str] = None
    live_stream: Optional[str] = None
    vpix: Optional[list] = None
    failover_host: Optional[str] = None
    high_thumbnail_url: Optional[str] = None
    hd_thumbnail_url: Optional[str] = None
    trailer: Optional[str] = None
    url_medium: Optional[str] = None
    url_provider: Optional[str] = None
    video_advertisement: Optional[dict] = None
    pin_count: Optional[int] = None
    annotations_info: Optional[dict] = None
