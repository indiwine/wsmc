from typing import Any

from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from .phonecheckrequest import PhoneCheckRequest


class GetFbPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        pass