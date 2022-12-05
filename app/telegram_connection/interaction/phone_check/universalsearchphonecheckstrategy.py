from typing import Any

from . import PhoneCheckRequest
from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from ..helpers.UniversalSearchMixin import UniversalSearchMixin


class UniversalSearchPhoneCheckStrategy(AbstractPhoneCheckStrategy, UniversalSearchMixin):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        chat = request.chat
        return self.collect_messages(self, chat, request.agent,
                                     lambda: request.agent.send_message_text(chat, request.phone))
