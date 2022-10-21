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

            sm_profile = self.get_or_create_sm_profile(request)
            self.assign_dto_to_obj(profile_dto, sm_profile)
            sm_profile.save()

        return super().handle(request)
