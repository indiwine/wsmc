from typing import Any

from .abstractemailcheckstrategy import AbstractEmailCheckStrategy
from .emailcheckrequest import EmailCheckRequest
from ..helpers.InfoBazaMixin import InfoBazaMixin


class InfobazaEmailCheckStrategy(AbstractEmailCheckStrategy, InfoBazaMixin):
    def do_interaction(self, request: EmailCheckRequest) -> Any:
        chat = request.chat
        return self.limit_search_collection(self, chat, request.agent,
                                            lambda: request.agent.send_message_text(chat, request.email))
