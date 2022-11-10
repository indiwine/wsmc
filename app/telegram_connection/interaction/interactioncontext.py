from typing import Any, Type

from .abstractinteractionrequest import AbstractInteractionRequest
from .abstractinteractionstrategy import AbstractInteractionStrategy
from ..bots.abstractbot import AbstractBot


class InteractionContext:
    def __init__(self, strategy: AbstractInteractionStrategy, bot: Type[AbstractBot]):
        self.strategy = strategy
        self.bot = bot

    def interact(self, request: AbstractInteractionRequest) -> Any:
        """
        Interact with the bot using `interaction_strategy`
        @param request: interaction request
        @return:
        """
        self._populate_chat(request)

        return self.strategy.do_interaction(request)

    def _populate_chat(self, request: AbstractInteractionRequest):
        request.set_chat(request.agent.find_chat_or_fail(self.bot.get_chat_name()))
