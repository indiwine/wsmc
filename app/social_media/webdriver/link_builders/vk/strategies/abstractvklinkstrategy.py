from abc import ABC, abstractmethod
from urllib.parse import urlparse

class AbstractVkLinkStrategy(ABC):
    base_url = 'https://vk.com'

    def __init__(self, profile_link: str, is_group: bool):
        self._original_profile_link = profile_link
        self._is_group = is_group

    @abstractmethod
    def get_profile_link(self) -> str:
        pass

    @abstractmethod
    def get_group_link(self) -> str:
        pass

    @abstractmethod
    def add_offset(self, url: str, offset: int) -> str:
        pass

    def get_last_path_component(self) -> str:
        parsed = urlparse(self._original_profile_link)
        return parsed.path.rsplit('/', 1)[-1]

