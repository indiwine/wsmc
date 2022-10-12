from social_media.models import SmPosts, CollectedPostsStats
from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...page_objects.fb import FacebookPostsPage
from ...request import Request


class FbPostsCollector(AbstractCollector):
    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            sm_profile = self.get_sm_profile(request)

            page = FacebookPostsPage(request.driver)

            for stats in CollectedPostsStats.objects.posts_to_check_generator(request.social_media_account):
                for post_dto in page.collect_posts(request.social_media_account.link, stats.date):
                    try:
                        sm_post = SmPosts.objects.get(sm_post_id=post_dto.sm_post_id,
                                                      profile=sm_profile,
                                                      social_media=post_dto.social_media)
                    except SmPosts.DoesNotExist:
                        sm_post = SmPosts(profile=sm_profile, suspect=request.social_media_account.suspect)

                    self.assign_dto_to_obj(post_dto, sm_post)
                    sm_post.save()

        return super().handle(request)
