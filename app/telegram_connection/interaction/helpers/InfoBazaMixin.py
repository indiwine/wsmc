from typing import Callable

from telegram_connection.agent import TgAgent
from telegram_connection.agent.responses import ChatResponse
from telegram_connection.interaction.abstractinteractionstrategy import AbstractInteractionStrategy


class InfoBazaMixin:
    @staticmethod
    def limit_search_collection(strategy: AbstractInteractionStrategy,
                                chat: ChatResponse,
                                agent: TgAgent,
                                send_cb: Callable):
        collect_predicate = strategy.get_same_chat_predicate(chat)

        stop_predicate = strategy.get_same_chat_with_text_predicate(chat, ['Ліміт пошуку', 'Перевищенно ліміт'])

        send_cb()
        messages = agent.wait_for_massage(collect_predicate, stop_predicate=stop_predicate)
        return strategy.messages_to_list(messages)
