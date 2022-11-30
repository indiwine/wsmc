from typing import Any

from .abstractemailcheckstrategy import AbstractEmailCheckStrategy
from .emailcheckrequest import EmailCheckRequest
from ..helpers.QuickOsintMixin import QuickOsintMixin


class QuickOsintEmailCheckStrategy(AbstractEmailCheckStrategy, QuickOsintMixin):
    def do_interaction(self, request: EmailCheckRequest) -> Any:
        chat = request.chat

        return self.collect_messages(self,
                                     chat,
                                     request.agent,
                                     lambda: request.agent.send_message_text(chat, request.email))
