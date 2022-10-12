from social_media.models import SmProfile
from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...page_objects.fb.facebookprofilegeneralpage import FacebookProfileGeneralPage
from ...request import Request


class FbProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            profile_dto = FacebookProfileGeneralPage(request.driver).collect_profile(request.social_media_account.link)

            try:
                sm_profile = self.get_sm_profile(request)
            except SmProfile.DoesNotExist:
                sm_profile = SmProfile(credentials=request.credentials, suspect=request.social_media_account.suspect)

            self.assign_dto_to_obj(profile_dto, sm_profile)

            sm_profile.save()

        return super().handle(request)
