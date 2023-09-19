from urllib import parse

from .abstractvklinkstrategy import AbstractVkLinkStrategy
from ....common import add_get_params_to_url


class BasicVkLinkStrategy(AbstractVkLinkStrategy):
    def get_group_link(self) -> str:
        if not self._is_group:
            raise RuntimeError('Trying to fetch group link form a profile strategy')
        return self._original_profile_link

    def get_profile_link(self) -> str:
        if self._is_group:
            raise RuntimeError('Trying to fetch profile link form a group strategy')
        return self._original_profile_link

    def add_offset(self, url: str, offset: int) -> str:
        return add_get_params_to_url(parse.urlparse(url), {'offset': offset})


