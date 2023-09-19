from typing import final

from .strategies.abstractvklinkstrategy import AbstractVkLinkStrategy
from .strategies.basicvklinkstrategy import BasicVkLinkStrategy


@final
class VkLinkBuilder:

    @staticmethod
    def build(profile_link: str) -> AbstractVkLinkStrategy:
        return BasicVkLinkStrategy(profile_link, is_group=False)

    @staticmethod
    def build_group(profile_link: str) -> AbstractVkLinkStrategy:
        return BasicVkLinkStrategy(profile_link, is_group=True)
