from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okloginpage import OkLoginPage
from ...request import Request


class OkLoginCollector(AbstractCollector):

    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.LOGIN, False):
            OkLoginPage(request.driver, OkLinkBuilder.build('')).perform_login(request.credentials.user_name,
                                                                               request.credentials.password)
        super().handle(request)
