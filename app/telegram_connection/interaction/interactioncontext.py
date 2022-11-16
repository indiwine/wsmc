from typing import Any, Type

from .abstractinteractionrequest import AbstractInteractionRequest
from .abstractinteractionstrategy import AbstractInteractionStrategy
from ..agent import TgAgent
from ..bots.abstractbot import AbstractBot


class InteractionContext:
    def __init__(self, strategy: AbstractInteractionStrategy,
                 bot: Type[AbstractBot],
                 request: AbstractInteractionRequest):
        self.strategy = strategy
        self.bot = bot
        self.request = request

    def interact(self, agent: TgAgent) -> Any:
        """
        Interact with the bot using `interaction_strategy`
        @return:
        """
        self.request.set_agent(agent)
        self._populate_chat(self.request)

        return self.strategy.do_interaction(self.request)

    def _populate_chat(self, request: AbstractInteractionRequest):
        request.set_chat(request.agent.find_chat_or_fail(self.bot.get_chat_name()))
