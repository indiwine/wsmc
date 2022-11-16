from typing import Any

from . import PhoneCheckRequest
from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy


class UniversalSearchPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        chat = request.chat
        request.agent.send_message_text(chat.id, request.phone)

        collect_predicate = self.get_same_chat_predicate(chat)

        stop_predicate = self.get_same_chat_with_text_predicate(chat, ['Вечная ссылка', 'Ссылка на бот'])

        messages = request.agent.wait_for_massage(collect_predicate, stop_predicate=stop_predicate, timeout=120.0)
        return self.messages_to_list(messages)
