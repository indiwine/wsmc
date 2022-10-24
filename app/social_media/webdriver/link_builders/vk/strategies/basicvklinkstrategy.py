from urllib import parse

from .abstractvklinkstrategy import AbstractVkLinkStrategy
from ....common import add_get_params_to_url


class BasicVkLinkStrategy(AbstractVkLinkStrategy):
    def get_profile_link(self) -> str:
        return self.original_profile_link

    def add_offset(self, url: str, offset: int) -> str:
        return add_get_params_to_url(parse.urlparse(url), {'offset': offset})
