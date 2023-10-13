from social_media.models import CollectedPostsStat
from social_media.social_media import SocialMediaActions
from ..abstractcollector import AbstractCollector
from ...link_builders.fb.fblinkbuilder import FbLinkBuilder
from ...page_objects.fb import FacebookPostsPage
from ...request import Request


class FbPostsCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaActions.POSTS):
            sm_profile = self.get_sm_profile(request)

            page = FacebookPostsPage(request.driver) \
                .set_navigation_strategy(FbLinkBuilder.build_strategy(request.target_url))

            for stats in CollectedPostsStat.objects.posts_to_check_generator(request.suspect_identity):
                for post_dto in page.collect_posts(stats.date):
                    self.persist_post(post_dto, sm_profile, request)

                stats.found = page.found_count
                stats.skipped = page.skip_count
                stats.finished = not stats.is_current_month
                stats.save()

        return super().handle(request)
