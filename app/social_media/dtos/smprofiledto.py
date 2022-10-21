import datetime
from dataclasses import dataclass
from typing import Union


@dataclass
class SmProfileDto:
    name: str
    location: str = None
    birthdate: Union[datetime.datetime, str] = None
    university: str = None
