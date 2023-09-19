from typing import Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.stream.entities.feedlikesummary import FeedLikeSummary


@nested_dataclass
class FeedGroupAlbum(BaseFeedEntity):
    def extract_body(self) -> Optional[str]:
        return self.title

    album_type: str
    aid: str
    title: str
    like_summary: FeedLikeSummary
    main_photo: dict
    is_competition: bool
