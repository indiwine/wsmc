from asgiref.sync import sync_to_async

from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkgrouppage import VkGroupPage
from ...request import Request


class VkGroupCollector(AbstractCollector):
    @sync_to_async
    def handle(self, request: Request):
        group_dto = VkGroupPage(request.driver, VkLinkBuilder.build_group(request.target_url)).collect_group()
        self.persist_group(group_dto, request, request.suspect_identity)
