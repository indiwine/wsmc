from abc import ABC, abstractmethod


class AbstractVkLinkStrategy(ABC):
    base_url = 'https://vk.com'

    def __init__(self, profile_link: str):
        self.original_profile_link = profile_link

    @abstractmethod
    def get_profile_link(self) -> str:
        pass
