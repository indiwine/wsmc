from abc import ABC, abstractmethod
from typing import Any

from .namecheckrequest import NameCheckRequest
from ..abstractinteractionstrategy import AbstractInteractionStrategy


class AbstractNameCheckStrategy(AbstractInteractionStrategy, ABC):
    @abstractmethod
    def do_interaction(self, request: NameCheckRequest) -> Any:
        pass
