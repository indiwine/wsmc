from .abstractvklinkstrategy import AbstractVkLinkStrategy


class BasicVkLinkStrategy(AbstractVkLinkStrategy):
    def get_profile_link(self) -> str:
        return self.original_profile_link
