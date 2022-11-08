import logging
from typing import List

from django.db import DEFAULT_DB_ALIAS

logger = logging.getLogger(__name__)


def manage_bots(
        app_config,
        verbosity=2,
        using=DEFAULT_DB_ALIAS,
        **kwargs,
):
    logger.info('Updating bots in database')
    from .models import TelegramBot

    existing_bots: List[str] = []
    for bot in TelegramBot.objects.all():
        existing_bots.append(bot.name)

    for loaded_bot in app_config.bots.keys():
        if loaded_bot not in existing_bots:
            TelegramBot.objects.create(name=loaded_bot)
            logger.info(f'New bot found: "{loaded_bot}"')
        else:
            existing_bots.remove(loaded_bot)

    if len(existing_bots) > 0:
        logger.info(f'Removing old bots: {",".join(existing_bots)}')
        TelegramBot.objects.filter(name__in=existing_bots).delete()
