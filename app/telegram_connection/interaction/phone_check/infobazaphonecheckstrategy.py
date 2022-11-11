from typing import Any

from . import PhoneCheckRequest
from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from ...agent.responses import MessageResponse


class InfoBazaPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        chat = request.chat
        request.agent.send_message_text(chat.id, request.phone)

        def collect_predicate(msg: MessageResponse):
            return msg.chat_id == chat.id and not msg.is_outgoing and msg.has_message_text

        def stop(msg: MessageResponse):
            end_msgs = [
                'Кількість'
            ]
            return collect_predicate(msg) and any(
                test_str in msg.message_text.palin_text for test_str in end_msgs)

        messages = request.agent.wait_for_massage(collect_predicate, stop_predicate=stop)
        return self.join_messages(messages)
