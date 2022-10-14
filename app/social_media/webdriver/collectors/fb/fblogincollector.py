from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.fb.fblinkbuilder import FbLinkBuilder
from ...page_objects.fb.facebookloginpage import FacebookLoginPage
from ...request import Request


class FbLoginCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.LOGIN, False):
            credentials = request.credentials

            FacebookLoginPage(request.driver) \
                .set_navigation_strategy(FbLinkBuilder.get_default_navigation_strategy('')) \
                .perform_login(credentials.user_name, credentials.password)
        return super().handle(request)
