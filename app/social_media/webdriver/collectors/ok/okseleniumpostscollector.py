from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.ok import OkLinkBuilder
from ...page_objects.ok.okpostspage import OkPostsPage
from ...request import Request


class OkSeleniumPostsCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            sm_profile = self.get_sm_profile(request)
            posts_page = OkPostsPage(request.driver, OkLinkBuilder.build(request.suspect_identity.link))
            for post in posts_page.collect_post():
                self.persist_post(post, sm_profile, request)

