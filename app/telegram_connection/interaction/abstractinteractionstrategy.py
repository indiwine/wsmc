from abc import ABC, abstractmethod
from typing import Any, List

from .abstractinteractionrequest import AbstractInteractionRequest
from ..agent.responses import MessageResponse


class AbstractInteractionStrategy(ABC):

    @abstractmethod
    def do_interaction(self, request: AbstractInteractionRequest) -> Any:
        """
        Make your interactions with the bot here
        @param request:
        """
        pass

    @staticmethod
    def join_messages(msgs: List[MessageResponse]) -> str:
        return '\n\n'.join(msg.message_text.palin_text for msg in msgs)
