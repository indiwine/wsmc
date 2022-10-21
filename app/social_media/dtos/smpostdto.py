import datetime as datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class SmPostDto:
    datetime: datetime.datetime
    sm_post_id: str = None
    social_media: str = None

    body: Optional[str] = None
    permalink: Optional[str] = None
    raw_post: Optional[dict] = None
