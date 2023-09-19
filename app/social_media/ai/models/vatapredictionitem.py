from dataclasses import dataclass
from typing import Literal

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class VataPredictionItem:
    x: int
    y: int
    width: int
    height: int
    label: Literal['z', 'v', 'colorado', 'russian_flag']
    pr: float
