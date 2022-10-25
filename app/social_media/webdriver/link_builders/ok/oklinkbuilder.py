from typing import final

from .strategies.abstractoklinkstrategy import AbstractOkLinkStrategy
from .strategies.basicoklinkstrategy import BasicOkLinkStrategy


@final
class OkLinkBuilder:
    @staticmethod
    def build(link_profile: str) -> AbstractOkLinkStrategy:
        return BasicOkLinkStrategy(link_profile)
