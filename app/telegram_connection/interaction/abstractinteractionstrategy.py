from abc import ABC, abstractmethod
from typing import Any

from .abstractinteractionrequest import AbstractInteractionRequest


class AbstractInteractionStrategy(ABC):

    @abstractmethod
    def do_interaction(self, request: AbstractInteractionRequest) -> Any:
        """
        Make your interactions with the bot here
        @param request:
        """
        pass
