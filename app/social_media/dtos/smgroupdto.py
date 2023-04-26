from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SmGroupDto:
    permalink: str
    oid: str
    name: str

    id: Optional[int] = field(default=None, metadata={'transient': True})
