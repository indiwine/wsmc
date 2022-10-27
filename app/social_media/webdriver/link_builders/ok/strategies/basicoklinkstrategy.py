from .abstractoklinkstrategy import AbstractOkLinkStrategy


class BasicOkLinkStrategy(AbstractOkLinkStrategy):
    def get_posts_page(self) -> str:
        return f'{self.profile_link}/statuses'

    def get_profile_about(self) -> str:
        return f'{self.profile_link}/about'
