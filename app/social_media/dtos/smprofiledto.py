import datetime
from typing import Union
from dataclasses import dataclass

@dataclass
class SmProfileDto:
    name: str
    location: str = None
    birthdate: Union[datetime.datetime, str] = None
    university: str = None