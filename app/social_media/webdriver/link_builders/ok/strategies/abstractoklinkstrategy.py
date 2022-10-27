from abc import ABC, abstractmethod


class AbstractOkLinkStrategy(ABC):
    basic_url = 'https://ok.ru'
    feed_url = 'https://ok.ru/feed'

    def __init__(self, profile_link: str):
        self.profile_link = profile_link

    @abstractmethod
    def get_profile_about(self) -> str:
        pass

    @abstractmethod
    def get_posts_page(self) -> str:
        pass
