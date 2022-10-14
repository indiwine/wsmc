from abc import ABC, abstractmethod
from urllib import parse


class AbstractFbLinkStrategy(ABC):
    base_url = 'https://www.facebook.com'

    def __init__(self, link: str):
        self.original_profile = link
        self._url = parse.urlparse(link)

    @abstractmethod
    def generate_profile_link(self) -> str:
        pass

    @abstractmethod
    def generate_about_profile_link(self) -> str:
        pass

    @abstractmethod
    def generate_basic_profile_info_link(self) -> str:
        pass

    @abstractmethod
    def generate_posts_link(self) -> str:
        pass
