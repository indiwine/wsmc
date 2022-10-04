from ..abstractcollector import AbstractCollector
from ...page_objects.fb.facebookloginpage import FacebookLoginPage
from ...request import Request
from social_media.social_media import SocialMediaEntities

class FbLoginCollector(AbstractCollector):
    def handle(self, request: Request):
        if SocialMediaEntities.LOGIN in request.entities:
            credentials = request.credentials
            FacebookLoginPage(request.driver).perform_login(credentials.user_name, credentials.password)
        return super().handle(request)

