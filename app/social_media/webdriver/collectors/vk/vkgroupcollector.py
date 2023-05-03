from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...request import Request
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkgrouppage import VkGroupPage


class VkGroupCollector(AbstractCollector):
    def handle(self, request: Request):
        group_dto = VkGroupPage(request.driver, VkLinkBuilder.build_group(request.target_url)).collect_group()
        self.persist_group(group_dto, request, request.suspect_identity)

        return super().handle(request)
