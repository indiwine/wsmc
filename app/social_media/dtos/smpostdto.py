import datetime as datetime
from dataclasses import dataclass, field
from typing import Optional, List

from .authordto import AuthorDto
from .smpostimagedto import SmPostImageDto


@dataclass
class SmPostDto:
    datetime: datetime.datetime

    author: AuthorDto = field(metadata={'transient': True})

    sm_post_id: str = None
    social_media: str = None

    body: Optional[str] = None
    permalink: Optional[str] = None
    raw_post: Optional[dict] = None

    id: Optional[int] = field(default=None, metadata={'transient': True})
    images: Optional[List[SmPostImageDto]] = field(default=None, metadata={'transient': True})
