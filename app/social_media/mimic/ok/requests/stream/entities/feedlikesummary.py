import dataclasses
from typing import Optional


@dataclasses.dataclass
class FeedLikeSummary:
    like_id: str
    like_possible: bool
    unlike_possible: bool
    use_default_reaction: bool
    count: Optional[int] = None
    self: Optional[bool] = None
    reactions: Optional[list] = None
    last_like_date_ms: Optional[int] = None
