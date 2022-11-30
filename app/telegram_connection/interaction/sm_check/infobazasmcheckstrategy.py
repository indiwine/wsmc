from typing import Any, List

from social_media.social_media import SocialMediaTypes
from .abstractsmcheckstrategy import AbstractSmCheckStrategy
from .smcheckrequest import SmCheckRequest


class InfoBazaSmCheckStrategy(AbstractSmCheckStrategy):
    @property
    def acceptable_social_media(self) -> List[SocialMediaTypes]:
        return [SocialMediaTypes.VK, SocialMediaTypes.FB]

    def interact_with_sm(self, profile: str, sm_type: SocialMediaTypes, request: SmCheckRequest) -> Any:
        pass