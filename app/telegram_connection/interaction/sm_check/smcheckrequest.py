from typing import List, Tuple

from ..abstractinteractionrequest import AbstractInteractionRequest
from social_media.social_media.socialmediatypes import SocialMediaTypes


class SmCheckRequest(AbstractInteractionRequest):
    check_stack: List[Tuple[str, SocialMediaTypes]] = []

    def add_sm(self, profile_url: str, sm: SocialMediaTypes):
        self.check_stack.append((profile_url, sm))