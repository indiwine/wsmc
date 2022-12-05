from typing import Any, List

from social_media.social_media import SocialMediaTypes
from .abstractsmcheckstrategy import AbstractSmCheckStrategy
from .smcheckrequest import SmCheckRequest
from ..helpers.UniversalSearchMixin import UniversalSearchMixin


class UniversalSearchSmCheckStrategy(AbstractSmCheckStrategy, UniversalSearchMixin):
    @property
    def acceptable_social_media(self) -> List[SocialMediaTypes]:
        return [SocialMediaTypes.OK, SocialMediaTypes.VK]

    def interact_with_sm(self, profile: str, sm_type: SocialMediaTypes, request: SmCheckRequest) -> Any:
        chat = request.chat
        return self.collect_messages(self, chat, request.agent, lambda: request.agent.send_message_text(chat, profile))
