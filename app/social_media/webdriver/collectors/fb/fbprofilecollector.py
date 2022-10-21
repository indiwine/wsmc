from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.fb.fblinkbuilder import FbLinkBuilder
from ...page_objects.fb.facebookprofilegeneralpage import FacebookProfileGeneralPage
from ...request import Request


class FbProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = FacebookProfileGeneralPage(request.driver) \
                .set_navigation_strategy(FbLinkBuilder.build_strategy(request.social_media_account.link)) \
                .collect_profile()

            sm_profile = self.get_or_create_sm_profile(request)
            self.assign_dto_to_obj(profile_dto, sm_profile)
            sm_profile.save()

        return super().handle(request)
