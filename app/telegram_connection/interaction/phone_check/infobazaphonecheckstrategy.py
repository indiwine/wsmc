from typing import Any

from . import PhoneCheckRequest
from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from ..helpers.InfoBazaMixin import InfoBazaMixin


class InfoBazaPhoneCheckStrategy(AbstractPhoneCheckStrategy, InfoBazaMixin):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        chat = request.chat
        request.agent.send_message_text(chat.id, request.phone)

        return self.limit_search_collection(self, chat, request.agent,
                                            lambda: request.agent.send_message_text(chat, request.phone))
