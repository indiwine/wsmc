from .abstractfblinkstrategy import AbstractFbLinkStrategy


class NickNameFbLinkStrategy(AbstractFbLinkStrategy):
    def generate_profile_link(self) -> str:
        return self.original_profile

    def generate_about_profile_link(self) -> str:
        return f'{self.original_profile}/about_overview'

    def generate_basic_profile_info_link(self) -> str:
        return f'{self.original_profile}/about_contact_and_basic_info'

    def generate_posts_link(self) -> str:
        return self.original_profile
