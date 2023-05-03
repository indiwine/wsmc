from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.fb.fblinkbuilder import FbLinkBuilder
from ...page_objects.fb.facebookprofilegeneralpage import FacebookProfileGeneralPage
from ...request import Request


class FbProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = FacebookProfileGeneralPage(request.driver) \
                .set_navigation_strategy(FbLinkBuilder.build_strategy(request.suspect_identity.link)) \
                .collect_profile()
            self.persist_sm_profile(profile_dto, request)

        return super().handle(request)
