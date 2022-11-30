from typing import Callable

from telegram_connection.agent import TgAgent
from telegram_connection.agent.responses import ChatResponse, MessageResponse
from telegram_connection.interaction.abstractinteractionstrategy import AbstractInteractionStrategy


class QuickOsintMixin:
    @staticmethod
    def collect_messages(
            strategy: AbstractInteractionStrategy,
            chat: ChatResponse,
            agent: TgAgent,
            send_cb: Callable):
        send_cb()
        same_chat_cb = strategy.get_same_chat_predicate(chat)

        def stop_predicate(msg: MessageResponse):
            if same_chat_cb(msg):
                if msg.has_message_text:
                    return '@Qu1ck_os11nt_bot' in msg.content.get_text
                if msg.has_reply_markup:
                    return msg.reply_markup.has_btn_with_text('Дополнительные методы поиска')
            return False

        messages = agent.wait_for_massage(same_chat_cb, stop_predicate=stop_predicate, timeout=60.0)
        return strategy.messages_to_list(messages)
