from abc import ABC, abstractmethod
from typing import Any

from .emailcheckrequest import EmailCheckRequest
from ..abstractinteractionstrategy import AbstractInteractionStrategy


class AbstractEmailCheckStrategy(AbstractInteractionStrategy, ABC):
    @abstractmethod
    def do_interaction(self, request: EmailCheckRequest) -> Any:
        pass
