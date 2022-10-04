from .collectors import Collector
from .collectors.fb import FbLoginCollector, FbProfileCollector
from .request import Request
from ..social_media import SocialMediaTypes


class Agent:
    def __init__(self, request: Request):
        self.request = request

    def run(self):
        try:
            self._construct_chain().handle(self.request)
        finally:
            self.request.close_driver()

    def _construct_chain(self) -> Collector:
        sm_type = self.request.credentials.social_media_type
        if sm_type == SocialMediaTypes.FB:
            login_handler = FbLoginCollector()
            login_handler.set_next(FbProfileCollector())
            return login_handler
        else:
            raise RuntimeError(f'No suitable chain for social media {sm_type}')
