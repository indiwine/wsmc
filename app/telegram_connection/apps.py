import logging
from importlib import import_module
from types import ModuleType

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.module_loading import module_has_submodule
from typing import Optional, Type

from .management import manage_bots
from telegram_connection.bots.abstractbot import AbstractBot
logger = logging.getLogger(__name__)

BOT_MODULE_NAME = 'bots'

class TelegramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_connection'
    verbose_name = 'Інтеграція з Telegram'
    bots_module: Optional[ModuleType] = None
    bots: dict[str, Type[AbstractBot]] = {}

    def ready(self):
        if module_has_submodule(self.module, BOT_MODULE_NAME):
            logger.debug(f'Bot module found')
            bot_module_name = "%s.%s" % (self.name, BOT_MODULE_NAME)
            self.bots_module = import_module(bot_module_name)
            for name, cls in self.bots_module.__dict__.items():
                if isinstance(cls, type) and issubclass(cls, AbstractBot):
                    bot_code = cls.get_code()
                    logger.debug(f'Found bot: "{bot_code}"')
                    self.bots[bot_code] = cls

        post_migrate.connect(manage_bots, sender=self)
