from dataclasses import dataclass, field
from typing import Optional, List

from social_media.ai.models.vatapredictionitem import VataPredictionItem


@dataclass
class SmPostImageDto:
    oid: str
    url: Optional[str] = None
    permalink: Optional[str] = None

    prediction: Optional[List[VataPredictionItem]] = None

    id: Optional[int] = field(default=None, metadata={'transient': True})
    created: Optional[bool] = field(default=None, metadata={'transient': True})
    tmpLocation: Optional[str] = field(default=None, metadata={'transient': True})
    """Will be populated after file been downloaded from Social media"""
