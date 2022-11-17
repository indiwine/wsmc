from typing import Any

from .abstractnamecheckstrategy import AbstractNameCheckStrategy
from .namecheckrequest import NameCheckRequest
from ...agent.responses import MessageResponse

NAME_BTN = 'Підписатись'


class OpenDataUABotNameCheckStrategy(AbstractNameCheckStrategy):
    def do_interaction(self, request: NameCheckRequest) -> Any:
        chat = request.chat
        same_chat_predicate = self.get_same_chat_predicate(chat)

        def stop(msg: MessageResponse):
            return same_chat_predicate(msg) and msg.has_reply_markup and msg.reply_markup.has_btn_with_text(NAME_BTN)

        request.agent.send_message_text(chat.id, request.name)
        msgs = request.agent.wait_for_massage(same_chat_predicate, stop_predicate=stop)
        return self.messages_to_list(msgs)
