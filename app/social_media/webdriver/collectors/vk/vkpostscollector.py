from typing import Generator, Optional, Callable

from social_media.dtos.smpostdto import SmPostDto
from social_media.dtos.smpostimagedto import SmPostImageDto
from social_media.models import VkPostStat, SmPost, SmProfile, SmPostImage
from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...request import Request


class VkPostsCollector(AbstractCollector):
    STEP: int = 20
    _max_offset: int

    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            sm_profile = self.get_sm_profile(request)
            wall = VkProfilePage(request.driver, VkLinkBuilder.build(request.social_media_account.link)).go_to_wall()
            has_posts = wall.wait_for_posts()
            if has_posts:
                self._max_offset = wall.get_max_offset()
                offset = 0
                try:
                    new_posts = 0
                    for offset in self._offset_generator(request, lambda: new_posts):

                        # resetting at each new offset
                        new_posts = 0
                        for post in wall.collect_posts(offset):
                            created = self._persist_post(post, sm_profile, request)
                            request.ee.emit('post', post)
                            if created:
                                new_posts += 1
                finally:
                    pass
                    # VkPostStat.objects.update_or_create(suspect_social_media=request.social_media_account,
                    #                                     defaults={'last_offset': offset})

        return super().handle(request)

    def _persist_post(self, post: SmPostDto, sm_profile: SmProfile, request: Request):
        saved_post, created = SmPost.objects.update_or_create(sm_post_id=post.sm_post_id,
                                                              profile=sm_profile,
                                                              social_media=post.social_media,
                                                              defaults={
                                                                  **self.as_dict_for_model(post),
                                                                  'profile': sm_profile,
                                                                  'suspect': request.social_media_account.suspect
                                                              })
        post.id = saved_post.id
        if post.images:
            for image in post.images:
                self._persist_image(image, saved_post)

        return created

    def _persist_image(self, image: SmPostImageDto, post: SmPost):
        saved_image, created = SmPostImage.objects.update_or_create(post=post, oid=image.oid, defaults={
            **self.as_dict_for_model(image),
            'post': post
        })
        image.id = saved_image.id
        image.created = created

    def _offset_generator(self, request: Request, new_amount_cb: Callable[[], int]) -> Generator[int, None, None]:
        last_offset: Optional[int] = None
        current_offset: int = 0
        try:
            post_stat = VkPostStat.objects.get(suspect_social_media=request.social_media_account)
            last_offset = post_stat.last_offset
        except VkPostStat.DoesNotExist:
            pass

        page = 0
        fwd_skipped = False
        while current_offset <= self._max_offset:
            yield current_offset
            new_posts = new_amount_cb()

            if not fwd_skipped and last_offset is not None and new_posts == 0:
                fwd_skipped = True
                current_offset = (page * self.STEP) + last_offset
                page = int(current_offset / self.STEP)
            else:
                current_offset += self.STEP
                page += 1
