from typing import Any, List

from social_media.social_media import SocialMediaTypes
from .abstractsmcheckstrategy import AbstractSmCheckStrategy
from .smcheckrequest import SmCheckRequest


class UniversalSearchSmCheckStrategy(AbstractSmCheckStrategy):
    @property
    def acceptable_social_media(self) -> List[SocialMediaTypes]:
        return [SocialMediaTypes.OK, SocialMediaTypes.VK]

    def interact_with_sm(self, profile: str, sm_type: SocialMediaTypes, request: SmCheckRequest) -> Any:
        pass