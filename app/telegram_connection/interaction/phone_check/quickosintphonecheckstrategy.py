from typing import Any

from . import PhoneCheckRequest
from .abstractphonecheckstrategy import AbstractPhoneCheckStrategy
from ...agent.responses import MessageResponse


class QuickOsintPhoneCheckStrategy(AbstractPhoneCheckStrategy):
    def do_interaction(self, request: PhoneCheckRequest) -> Any:
        chat = request.chat
        request.agent.send_message_text(chat.id, request.phone)

        same_chat_cb = self.get_same_chat_predicate(chat)

        def stop_predicate(msg: MessageResponse):
            if same_chat_cb(msg):
                if msg.has_message_text:
                    return '@Qu1ck_os11nt_bot' in msg.content.get_text
                if msg.has_reply_markup:
                    return msg.reply_markup.has_btn_with_text('Дополнительные методы поиска')
            return False

        messages = request.agent.wait_for_massage(same_chat_cb, stop_predicate=stop_predicate, timeout=60.0)
        return self.messages_to_list(messages)
