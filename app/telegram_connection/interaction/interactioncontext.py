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
        return self.strategy.do_interaction(request)
