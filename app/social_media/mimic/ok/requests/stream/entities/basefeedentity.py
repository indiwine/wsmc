import abc
import dataclasses
from typing import Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.feedlikesummary import FeedLikeSummary


@dataclasses.dataclass
class BaseFeedEntity:
    ref: str

    @abc.abstractmethod
    def extract_body(self) -> Optional[str]:
        """
        Extract body from entity
        @return:
        """
        pass

    def extract_permalink(self) -> Optional[str]:
        if hasattr(self, 'reshare_summary') and self.reshare_summary is not None:
            return self.reshare_summary.reshare_external_link
        return None

    def extract_like_summary(self) -> Optional[FeedLikeSummary]:
        if hasattr(self, 'like_summary'):
            return self.like_summary
        return None
