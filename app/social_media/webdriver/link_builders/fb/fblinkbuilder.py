from typing import final
from urllib.parse import urlparse

from .strategies.abstractfblinkstrategy import AbstractFbLinkStrategy
from .strategies.idstrategy import IdFbLinkStrategy
from .strategies.nicknamestrategy import NickNameFbLinkStrategy


@final
class FbLinkBuilder:

    @staticmethod
    def build_strategy(profile_url: str) -> AbstractFbLinkStrategy:
        url = urlparse(profile_url)
        if url.path.find('/profile.php') >= 0:
            return IdFbLinkStrategy(profile_url)
        else:
            return FbLinkBuilder.get_default_navigation_strategy(profile_url)

    @staticmethod
    def get_default_navigation_strategy(profile_url: str) -> AbstractFbLinkStrategy:
        return NickNameFbLinkStrategy(profile_url)
