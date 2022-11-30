from typing import Any, List

from social_media.social_media import SocialMediaTypes
from .abstractsmcheckstrategy import AbstractSmCheckStrategy
from .smcheckrequest import SmCheckRequest
from ..helpers.QuickOsintMixin import QuickOsintMixin


class QuickOsintSmCheckStrategy(AbstractSmCheckStrategy, QuickOsintMixin):
    @property
    def acceptable_social_media(self) -> List[SocialMediaTypes]:
        return [SocialMediaTypes.FB, SocialMediaTypes.VK]

    def interact_with_sm(self, profile: str, sm_type: SocialMediaTypes, request: SmCheckRequest) -> Any:
        return self.collect_messages(self, request.chat, request.agent,
                                     lambda: request.agent.send_message_text(request.chat, profile))
