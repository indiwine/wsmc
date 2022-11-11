import logging
from copy import copy
from typing import List, Tuple, Type, Any

from telegram_connection.agent import TgAgent
from telegram_connection.bots.abstractbot import AbstractBot
from telegram_connection.bots import GetFbBot, UniversalSearchBot
from telegram_connection.interaction.abstractinteractionstrategy import AbstractInteractionStrategy
from telegram_connection.interaction.phone_check import GetFbPhoneCheckStrategy, PhoneCheckRequest, UniversalSearchPhoneCheckStrategy
from telegram_connection.models import TelegramAccount
from .abstractinteractionrequest import AbstractInteractionRequest
from .interactioncontext import InteractionContext

logger = logging.getLogger(__name__)
BotMapType = List[Tuple[Type[AbstractBot], Type[AbstractInteractionStrategy]]]
InterationResultType = List[Tuple[InteractionContext, Any]]


class TgAgentContext:
    def __init__(self, agent: TgAgent):
        self.agent = agent
        self.interaction_contexts: List[InteractionContext] = []

    def add_interaction_context(self, ct: InteractionContext):
        self.interaction_contexts.append(ct)

    def apply(self, request: AbstractInteractionRequest) -> InterationResultType:
        cp = copy(request)
        results = []
        for interaction_context in self.interaction_contexts:
            results.append((interaction_context, interaction_context.interact(cp)))
        return results


class BotBuilder:
    _PHONE_MAP: BotMapType = [
        (GetFbBot, GetFbPhoneCheckStrategy),
        (UniversalSearchBot, UniversalSearchPhoneCheckStrategy)
    ]

    @staticmethod
    def build_phone_check_contexts() -> List[InteractionContext]:
        contexts = []
        for Bot, Strategy in BotBuilder._PHONE_MAP:
            contexts.append(InteractionContext(Strategy(), Bot))
        return contexts

    @staticmethod
    def build_tg_contexts(contexts: List[InteractionContext]) -> List[TgAgentContext]:
        bot_codes = map(lambda ct: ct.bot.get_code(), contexts)
        tg_accounts = TelegramAccount.objects.filter(bots_to_use__code__in=bot_codes, logged_in=True).distinct()

        agent_contexts: List[TgAgentContext] = []
        for tg_account in tg_accounts:
            tg_context = TgAgentContext(TgAgent(tg_account))
            for bot in tg_account.bots_to_use.all():
                try:
                    interaction_context = next(ct for ct in contexts if ct.bot.get_code() == bot.code)
                    tg_context.add_interaction_context(interaction_context)
                    contexts.remove(interaction_context)
                except StopIteration:
                    logging.debug(f'No interaction context for BOT {bot.__str__()} found')

            agent_contexts.append(tg_context)

        return agent_contexts

    @staticmethod
    def check_phone(phone: str, name: str) -> InterationResultType:
        contexts = BotBuilder.build_phone_check_contexts()
        if len(contexts) == 0:
            return []

        agent_contexts = BotBuilder.build_tg_contexts(contexts)

        try:
            for tg_context in agent_contexts:
                tg_context.agent.login_or_fail()

            results = []
            for tg_context in agent_contexts:
                check_request = PhoneCheckRequest(tg_context.agent)
                check_request.set_arguments(phone, name)
                results = results + tg_context.apply(check_request)

            return results
        finally:
            for tg_context in agent_contexts:
                tg_context.agent.stop()
