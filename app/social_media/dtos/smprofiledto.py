import datetime
from dataclasses import dataclass, field
from typing import Union, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SmProfileMetadata:
    mobile_phone: str = None
    twitter: str = None
    site: str = None
    permalink: str = None


@dataclass
class SmProfileDto:
    name: str
    oid: str

    location: str = None
    birthdate: Union[datetime.datetime, str] = None
    university: str = None
    home_town: str = None
    country: str = field(default=None, metadata={'transient': True})
    domain: str = None
    metadata: Optional[SmProfileMetadata] = None
