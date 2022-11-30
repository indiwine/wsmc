import logging
from typing import List, Tuple, Type, Any, Dict

from telegram_connection.agent import TgAgent
from telegram_connection.bots import GetFbBot, UniversalSearchBot, InfoBazaBot, QuickOsintBot, OpenDataUABot
from telegram_connection.bots.abstractbot import AbstractBot
from telegram_connection.models import TelegramAccount
from .abstractinteractionrequest import AbstractInteractionRequest
from .abstractinteractionstrategy import AbstractInteractionStrategy
from .email_check import InfobazaEmailCheckStrategy, QuickOsintEmailCheckStrategy
from .email_check.emailcheckrequest import EmailCheckRequest
from .interactioncontext import InteractionContext
from .name_check import InfoBazaNameCheckStrategy, OpenDataUABotNameCheckStrategy
from .name_check.namecheckrequest import NameCheckRequest
from .phone_check import GetFbPhoneCheckStrategy, PhoneCheckRequest, \
    UniversalSearchPhoneCheckStrategy, InfoBazaPhoneCheckStrategy, QuickOsintPhoneCheckStrategy
from .sm_check.smcheckrequest import SmCheckRequest
from .sm_check import QuickOsintSmCheckStrategy

logger = logging.getLogger(__name__)
BotMapType = List[Tuple[Type[AbstractBot], Type[AbstractInteractionStrategy]]]
InterationResultType = List[Tuple[InteractionContext, Any]]
BotInterationType = Dict[Type[AbstractBot], List[InteractionContext]]


class TgAgentContext:
    def __init__(self, agent: TgAgent):
        self.agent = agent
        self.interaction_contexts: List[InteractionContext] = []

    def add_contexts(self, ctx: List[InteractionContext]):
        self.interaction_contexts = self.interaction_contexts + ctx

    def apply(self) -> InterationResultType:
        results = []
        for interaction_context in self.interaction_contexts:
            results.append((interaction_context, interaction_context.interact(self.agent)))
        return results


class BotBuilder:
    _PHONE_MAP: BotMapType = [
        (GetFbBot, GetFbPhoneCheckStrategy),
        (UniversalSearchBot, UniversalSearchPhoneCheckStrategy),
        (InfoBazaBot, InfoBazaPhoneCheckStrategy),
        (QuickOsintBot, QuickOsintPhoneCheckStrategy)
    ]

    _EMAIL_MAP: BotMapType = [
        (InfoBazaBot, InfobazaEmailCheckStrategy),
        (QuickOsintBot, QuickOsintEmailCheckStrategy)
    ]

    _NAME_MAP: BotMapType = [
        (InfoBazaBot, InfoBazaNameCheckStrategy),
        (OpenDataUABot, OpenDataUABotNameCheckStrategy)
    ]

    _SM_MAP: BotMapType = [
        (QuickOsintBot, QuickOsintSmCheckStrategy)
    ]

    @classmethod
    def build_interaction_contexts(cls, check_requests: List[AbstractInteractionRequest]) -> BotInterationType:
        result = {}
        logger.debug('Building contexts')

        def append_from_map(bot_map: BotMapType, in_request: AbstractInteractionRequest):
            for Bot, Strategy in bot_map:
                if Bot not in result:
                    result[Bot] = []
                result[Bot].append(InteractionContext(Strategy(), Bot, in_request))

        for request in check_requests:
            if isinstance(request, PhoneCheckRequest):
                append_from_map(cls._PHONE_MAP, request)
            elif isinstance(request, NameCheckRequest):
                append_from_map(cls._NAME_MAP, request)
            elif isinstance(request, EmailCheckRequest):
                append_from_map(cls._EMAIL_MAP, request)
            elif isinstance(request, SmCheckRequest):
                append_from_map(cls._SM_MAP, request)
        return result

    @classmethod
    def process_requests(cls, check_requests: List[AbstractInteractionRequest]) -> InterationResultType:
        interation_contexts = cls.build_interaction_contexts(check_requests)
        if len(interation_contexts) == 0:
            return []

        agent_contexts = cls.build_tg_contexts(interation_contexts)

        try:
            for tg_context in agent_contexts:
                tg_context.agent.login_or_fail()
                tg_context.agent.refresh_chats()

            results = []
            for tg_context in agent_contexts:
                results = results + tg_context.apply()

            return results
        finally:
            for tg_context in agent_contexts:
                tg_context.agent.stop()

    @staticmethod
    def build_tg_contexts(contexts: BotInterationType) -> List[TgAgentContext]:
        bot_codes = list(map(lambda ct: ct.get_code(), contexts.keys()))
        tg_accounts = TelegramAccount.objects.filter(bots_to_use__code__in=bot_codes, logged_in=True).distinct()

        agent_contexts: List[TgAgentContext] = []
        for tg_account in tg_accounts:
            tg_context = TgAgentContext(TgAgent(tg_account))
            for bot in tg_account.bots_to_use.all():
                try:
                    bot_ref = next(ct for ct in contexts.keys() if ct.get_code() == bot.code)
                    tg_context.add_contexts(contexts[bot_ref])
                except StopIteration:
                    logger.debug(f'No interaction context for BOT {bot.__str__()} found')

            agent_contexts.append(tg_context)

        return agent_contexts
