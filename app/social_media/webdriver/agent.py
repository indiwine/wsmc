import logging

from .collectors import Collector
from .collectors.fb import FbLoginCollector, FbProfileCollector, FbPostsCollector
from .collectors.ok import OkLoginCollector, OkProfileCollector, OkPostsCollector
from .collectors.vk import VkLoginCollector, VkProfileCollector, VkPostsCollector
from .request import Request
from ..social_media import SocialMediaTypes

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, request: Request):
        self.request = request
        logger.info(f'Agent created for {request}')

    def run(self):
        logger.info('Starting Agent')
        try:
            self._construct_chain().handle(self.request)
        finally:
            self.request.close_driver()

    def _construct_chain(self) -> Collector:
        sm_type = self.request.credentials.social_media
        logger.info(f'Generating chain for {sm_type}')
        if sm_type == SocialMediaTypes.FB:
            login_handler = FbLoginCollector()
            login_handler.set_next(FbProfileCollector().set_next(FbPostsCollector()))
            return login_handler
        elif sm_type == SocialMediaTypes.VK:
            login_handler = VkLoginCollector()
            login_handler.set_next(VkProfileCollector().set_next(VkPostsCollector()))
            return login_handler
        elif sm_type == SocialMediaTypes.OK:
            login_handler = OkLoginCollector()
            login_handler.set_next(OkProfileCollector().set_next(OkPostsCollector()))
            return login_handler
        else:
            raise RuntimeError(f'No suitable chain for social media {sm_type}')
