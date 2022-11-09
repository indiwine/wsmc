import logging
from pprint import pprint
from typing import List


from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS, connection

logger = logging.getLogger(__name__)


def manage_bots(
        app_config: AppConfig,
        verbosity=2,
        using=DEFAULT_DB_ALIAS,
        **kwargs,
):
    logger.info('Updating bots in database')
    from .models import TelegramBot

    existing_bots: List[str] = []
    for bot in TelegramBot.objects.all():
        existing_bots.append(bot.code)

    for loaded_bot_code, bot_cls in app_config.bots.items():
        bot_name = bot_cls.get_name()
        if loaded_bot_code not in existing_bots:
            TelegramBot.objects.create(code=loaded_bot_code, name=bot_name)
            logger.info(f'New bot found: "{loaded_bot_code}"')
        else:
            TelegramBot.objects.filter(code=loaded_bot_code).update(name=bot_name)
            existing_bots.remove(loaded_bot_code)

    if len(existing_bots) > 0:
        logger.info(f'Removing old bots: {",".join(existing_bots)}')
        TelegramBot.objects.filter(code__in=existing_bots).delete()
