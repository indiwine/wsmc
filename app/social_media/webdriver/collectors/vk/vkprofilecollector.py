from asgiref.sync import sync_to_async

from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...request import Request


class VkProfileCollector(AbstractCollector):
    @sync_to_async
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.PROFILE):
            profile_dto = VkProfilePage(request.driver, VkLinkBuilder.build(request.target_url)) \
                .collect_profile()

            self.persist_sm_profile(profile_dto, request)
