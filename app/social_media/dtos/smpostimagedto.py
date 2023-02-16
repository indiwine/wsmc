from dataclasses import dataclass
from typing import Optional


@dataclass
class SmPostImageDto:
    oid: str
    url: Optional[str] = None