import logging

from .collectors import Collector
from .collectors.fb import FbLoginCollector, FbProfileCollector, FbPostsCollector
from .collectors.ok import OkLoginCollector, OkProfileCollector, OkPostsCollector
from .collectors.vk import VkLoginCollector, VkProfileCollector, VkPostsCollector, VkSecondaryProfilesCollector, \
    VkGroupCollector
from .request import Request
from ..social_media import SocialMediaTypes, SocialMediaEntities

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
            self.close_driver()

    def close_driver(self):
        self.request.close_driver()

    def _construct_chain(self) -> Collector:
        sm_type = self.request.get_social_media_type
        logger.info(f'Generating chain for {sm_type}')
        if sm_type == SocialMediaTypes.FB:
            login_handler = FbLoginCollector()
            login_handler.set_next(FbProfileCollector().set_next(FbPostsCollector()))
            return login_handler
        elif sm_type == SocialMediaTypes.VK:

            stack = []

            if self.request.has_entity(SocialMediaEntities.LOGIN):
                stack.append(VkLoginCollector())

            if self.request.has_entity(SocialMediaEntities.PROFILE):
                stack.append(VkProfileCollector())

            if self.request.has_entity(SocialMediaEntities.GROUP):
                stack.append(VkGroupCollector())

            if self.request.has_entity(SocialMediaEntities.POSTS):
                stack.append(VkPostsCollector())

            if self.request.has_entity(SocialMediaEntities.UNKNOWN_PROFILES):
                stack.append(VkSecondaryProfilesCollector())

            base = stack.pop(0)

            previous_element = base
            while len(stack) > 0:
                current_elem = stack.pop(0)
                previous_element.set_next(current_elem)
                previous_element = current_elem

            return base

        elif sm_type == SocialMediaTypes.OK:
            login_handler = OkLoginCollector()
            login_handler.set_next(OkProfileCollector().set_next(OkPostsCollector()))
            return login_handler
        else:
            raise RuntimeError(f'No suitable chain for social media {sm_type}')
