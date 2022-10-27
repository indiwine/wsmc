from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okaboutprofilepage import OkAboutProfilePage
from ...request import Request


class OkProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = OkAboutProfilePage(request.driver,
                                             OkLinkBuilder.build(request.social_media_account.link)).collect_data()
            sm_profile = self.get_or_create_sm_profile(request)
            self.assign_dto_to_obj(profile_dto, sm_profile)
            sm_profile.save()

        super().handle(request)
