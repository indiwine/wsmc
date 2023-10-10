from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okloginpage import OkLoginPage
from ...request import Request


class OkSeleniumLoginCollector(AbstractCollector):
    """
    :deprecated
    """
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.LOGIN, False):
            OkLoginPage(request.driver, OkLinkBuilder.build('')).perform_login(request.credentials.user_name,
                                                                               request.credentials.password)
