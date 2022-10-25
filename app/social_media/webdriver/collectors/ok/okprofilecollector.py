from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ... import Request


class OkProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.PROFILE):
            pass

        super().handle(request)
