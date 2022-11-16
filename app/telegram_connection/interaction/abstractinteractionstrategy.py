from abc import ABC, abstractmethod
from functools import partial
from typing import Any, List

from .abstractinteractionrequest import AbstractInteractionRequest
from ..agent.responses import MessageResponse, ChatResponse
from ..agent.tgagent import MessageResponsePredicate


class AbstractInteractionStrategy(ABC):

    @abstractmethod
    def do_interaction(self, request: AbstractInteractionRequest) -> Any:
        """
        Make your interactions with the bot here
        @param request:
        """
        pass

    @staticmethod
    def filter_has_text(msgs: List[MessageResponse]):
        return filter(lambda msg: msg.has_message_text, msgs)

    @staticmethod
    def messages_to_list(msgs: List[MessageResponse]) -> List[str]:
        return list(map(lambda msg: msg.content.get_text, AbstractInteractionStrategy.filter_has_text(msgs)))

    @staticmethod
    def is_same_chat(bound_chat: ChatResponse, msg: MessageResponse) -> bool:
        return msg.chat_id == bound_chat.id and not msg.is_outgoing

    @staticmethod
    def get_same_chat_predicate(chat: ChatResponse) -> MessageResponsePredicate:
        return partial(AbstractInteractionStrategy.is_same_chat, chat)

    @staticmethod
    def get_same_chat_with_text_predicate(chat: ChatResponse, phrases: List[str]) -> MessageResponsePredicate:
        def stop(same_chat_predicate: MessageResponsePredicate, end_phrases: List[str], msg: MessageResponse):
            return same_chat_predicate(msg) and any(
                test_str in msg.message_text.palin_text for test_str in end_phrases)

        return partial(stop, AbstractInteractionStrategy.get_same_chat_predicate(chat), phrases)
