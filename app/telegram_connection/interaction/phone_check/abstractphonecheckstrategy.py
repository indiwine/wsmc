from abc import ABC, abstractmethod
from typing import Any

from .phonecheckrequest import PhoneCheckRequest
from ..abstractinteractionstrategy import AbstractInteractionStrategy


class AbstractPhoneCheckStrategy(AbstractInteractionStrategy, ABC):
    @abstractmethod
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        pass
