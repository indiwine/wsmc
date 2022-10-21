from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...request import Request
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkprofilepage import VkProfilePage


class VkPostsCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            wall = VkProfilePage(request.driver, VkLinkBuilder.build(request.social_media_account.link))\
                .go_to_wall()


        return super().handle(request)
