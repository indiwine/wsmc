from typing import Any

from .abstractemailcheckstrategy import AbstractEmailCheckStrategy
from .emailcheckrequest import EmailCheckRequest


class InfobazaEmailCheckStrategy(AbstractEmailCheckStrategy):
    def do_interaction(self, request: EmailCheckRequest) -> Any:
        chat = request.chat
        request.agent.send_message_text(chat.id, request.email)

        collect_predicate = self.get_same_chat_predicate(chat)

        stop_predicate = self.get_same_chat_with_text_predicate(chat, ['Ліміт пошуку'])

        messages = request.agent.wait_for_massage(collect_predicate, stop_predicate=stop_predicate)
        return self.messages_to_list(messages)
