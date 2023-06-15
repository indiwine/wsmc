import logging
from random import randint
from time import sleep

from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...options.vkoptions import VkOptions
from ...page_objects.vk import VkLoginPage
from ...request import Request

logger = logging.getLogger(__name__)


class VkLoginCollector(AbstractCollector):
    MAX_JITTER_DELAY = 5 * 60
    MIN_JITTER_DELAY = 15
    _options: VkOptions = None

    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.LOGIN, False):
            if self._options.login_use_jitter:
                delay = randint(self.MIN_JITTER_DELAY, self.MAX_JITTER_DELAY)
                logger.debug(f'Login delay jitter is active, waiting for {delay}s before login')
                sleep(delay)

            VkLoginPage(request.driver, VkLinkBuilder.build('')) \
                .perform_login(request.credentials.user_name, request.credentials.password)

        return super().handle(request)
