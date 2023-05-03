from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okaboutprofilepage import OkAboutProfilePage
from ...request import Request


class OkProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = OkAboutProfilePage(request.driver,
                                             OkLinkBuilder.build(request.suspect_identity.link)).collect_data()
            self.persist_sm_profile(profile_dto, request)

        super().handle(request)
