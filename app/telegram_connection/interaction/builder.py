from typing import List, Tuple, Type

from telegram_connection.bots.abstractbot import AbstractBot
from telegram_connection.bots.getfbbot import GetFbBot
from telegram_connection.interaction.abstractinteractionstrategy import AbstractInteractionStrategy
from telegram_connection.interaction.phone_check import GetFbPhoneCheckStrategy
from .interactioncontext import InteractionContext

BotMapType = List[Tuple[Type[AbstractBot], Type[AbstractInteractionStrategy]]]


class BotBuilder:
    _PHONE_MAP: BotMapType = [
        (GetFbBot, GetFbPhoneCheckStrategy)
    ]

    @staticmethod
    def build_phone_check_bots() -> List[InteractionContext]:
        contexts = []
        for Bot, Strategy in BotBuilder._PHONE_MAP:
            contexts.append(InteractionContext(Strategy(), Bot))
        return contexts
