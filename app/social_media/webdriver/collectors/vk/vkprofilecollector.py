from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...link_builders.vk import VkLinkBuilder
from ...request import Request


class VkProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = VkProfilePage(request.driver, VkLinkBuilder.build(request.social_media_account.link))\
                .collect_profile()

            self.persist_sm_profile(profile_dto, request)
        return super().handle(request)
