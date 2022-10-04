import dataclasses

from social_media.models import SmProfile
from ..abstractcollector import AbstractCollector
from ...request import Request
from social_media.social_media import SocialMediaEntities
from ...page_objects.fb.facebookprofilegeneralpage import FacebookProfileGeneralPage

class FbProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.social_media_account is not None and SocialMediaEntities.PROFILE in request.entities:
            profile_dto = FacebookProfileGeneralPage(request.driver).collect_profile(request.social_media_account.link)

            try:
                sm_profile = SmProfile.objects.get(credentials=request.credentials, suspect=request.social_media_account.suspect)
            except SmProfile.DoesNotExist:
                sm_profile = SmProfile(credentials=request.credentials, suspect=request.social_media_account.suspect)

            for key, value in dataclasses.asdict(profile_dto).items():
                setattr(sm_profile, key, value)

            sm_profile.save()

        return super().handle(request)
