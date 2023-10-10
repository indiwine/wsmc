import logging
from random import randint
from time import sleep

from asgiref.sync import sync_to_async

from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...options.vkoptions import VkOptions
from ...page_objects.vk import VkLoginPage
from ...request import Request

logger = logging.getLogger(__name__)


class VkLoginCollector(AbstractCollector[None, VkOptions]):
    MAX_JITTER_DELAY = 1 * 60
    MIN_JITTER_DELAY = 15

    # _options: VkOptions = None

    @sync_to_async
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.LOGIN, False):
            if self.get_options().login_use_jitter:
                delay = randint(self.MIN_JITTER_DELAY, self.MAX_JITTER_DELAY)
                logger.debug(f'Login delay jitter is active, waiting for {delay}s before login')
                sleep(delay)

            VkLoginPage(request.driver, VkLinkBuilder.build('')) \
                .perform_login(request.credentials.user_name, request.credentials.password)
