from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okaboutprofilepage import OkAboutProfilePage
from ...request import Request


class OkSeleniumProfileCollector(AbstractCollector):
    """
    :deprecated
    """
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.PROFILE):
            profile_dto = OkAboutProfilePage(request.driver,
                                             OkLinkBuilder.build(request.target_url)).collect_data()
            self.persist_sm_profile(profile_dto, request)

