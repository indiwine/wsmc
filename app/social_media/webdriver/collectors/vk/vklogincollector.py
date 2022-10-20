from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...request import Request

from ...page_objects.vk import VkLoginPage


class VkLoginCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.LOGIN, False):
            VkLoginPage(request.driver)\
                .perform_login(request.credentials.user_name, request.credentials.password)

        return super().handle(request)