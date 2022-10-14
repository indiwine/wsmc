import urllib.parse

from .abstractfblinkstrategy import AbstractFbLinkStrategy


class IdFbLinkStrategy(AbstractFbLinkStrategy):
    def generate_profile_link(self) -> str:
        return self.original_profile

    def generate_about_profile_link(self) -> str:
        return self._add_to_url({'sk': 'about_overview'})

    def generate_basic_profile_info_link(self) -> str:
        return self._add_to_url({'sk': 'about_contact_and_basic_info'})

    def generate_posts_link(self) -> str:
        return self.original_profile

    def _add_to_url(self, params: dict) -> str:
        url_parts = list(self._url)
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(url_parts)
