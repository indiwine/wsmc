from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.fb.fblinkbuilder import FbLinkBuilder
from ...page_objects.fb.facebookprofilegeneralpage import FacebookProfileGeneralPage
from ...request import Request


class FbProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.PROFILE):
            profile_dto = FacebookProfileGeneralPage(request.driver) \
                .set_navigation_strategy(FbLinkBuilder.build_strategy(request.target_url)) \
                .collect_profile()
            self.persist_sm_profile(profile_dto, request)

