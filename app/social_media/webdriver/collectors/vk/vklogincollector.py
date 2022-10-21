from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk import VkLoginPage
from ...request import Request


class VkLoginCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.LOGIN, False):
            VkLoginPage(request.driver, VkLinkBuilder.build('')) \
                .perform_login(request.credentials.user_name, request.credentials.password)

        return super().handle(request)
