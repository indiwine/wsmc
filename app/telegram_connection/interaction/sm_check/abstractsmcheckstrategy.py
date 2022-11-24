from abc import ABC, abstractmethod
from typing import Any, List

from social_media.social_media.socialmediatypes import SocialMediaTypes
from .smcheckrequest import SmCheckRequest
from ..abstractinteractionstrategy import AbstractInteractionStrategy


class AbstractSmCheckStrategy(AbstractInteractionStrategy, ABC):
    @abstractmethod
    @property
    def acceptable_social_media(self) -> List[SocialMediaTypes]:
        pass

    @abstractmethod
    def interact_with_sm(self, profile: str, sm_type: SocialMediaTypes, request: SmCheckRequest) -> Any:
        pass

    def do_interaction(self, request: SmCheckRequest) -> Any:
        result = []
        sm_types = self.acceptable_social_media

        for profile, sm in request.check_stack:
            if sm in sm_types:
                result.append((sm, self.interact_with_sm(profile, sm, request)))

        return result
