from typing import Any

from .abstractnamecheckstrategy import AbstractNameCheckStrategy
from .namecheckrequest import NameCheckRequest
from ...agent.responses import MessageResponse

NAME_BTN = 'ПІБ'


class InfoBazaNameCheckStrategy(AbstractNameCheckStrategy):
    def do_interaction(self, request: NameCheckRequest) -> Any:
        chat = request.chat
        same_chat_predicate = self.get_same_chat_predicate(chat)

        def wait_for_bot_request(msg: MessageResponse):
            return same_chat_predicate(msg) and msg.has_reply_markup and msg.reply_markup.has_btn_with_text(NAME_BTN)

        request.agent.send_message_text(chat.id, request.name)
        request_msgs = request.agent.wait_for_massage(wait_for_bot_request, stop_predicate=wait_for_bot_request)
        if len(request_msgs) == 0:
            return None
        request_msg = request_msgs[0]
        btn = request_msg.reply_markup.find_btn_by_text(NAME_BTN)
        if btn is None:
            return None

        request.agent.get_callback_query_answer(request_msg, btn.data)

        stop_predicate = self.get_same_chat_with_text_predicate(chat, [request.name, 'Нічого не знайшов'])
        msgs = request.agent.wait_for_massage(same_chat_predicate, stop_predicate=stop_predicate)
        return self.messages_to_list(msgs)