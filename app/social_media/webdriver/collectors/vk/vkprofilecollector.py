from asgiref.sync import sync_to_async

from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...request import Request


class VkProfileCollector(AbstractCollector):
    @sync_to_async
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = VkProfilePage(request.driver, VkLinkBuilder.build(request.suspect_identity.link)) \
                .collect_profile()

            self.persist_sm_profile(profile_dto, request)
