from .abstractfblinkstrategy import AbstractFbLinkStrategy
from ....common import add_get_params_to_url


class IdFbLinkStrategy(AbstractFbLinkStrategy):
    def generate_profile_link(self) -> str:
        return self.original_profile

    def generate_about_profile_link(self) -> str:
        return add_get_params_to_url(self._url, {'sk': 'about_overview'})

    def generate_basic_profile_info_link(self) -> str:
        return add_get_params_to_url(self._url, {'sk': 'about_contact_and_basic_info'})

    def generate_posts_link(self) -> str:
        return self.original_profile
