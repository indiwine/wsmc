import logging
from typing import Generator, Optional, Callable, Tuple

from selenium.common import ElementNotInteractableException

from social_media.models import VkPostStat, SmPost
from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...exceptions import WsmcStopPostCollection
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkgrouppage import VkGroupPage
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...page_objects.vk.vkprofilewallpage import VkProfileWallPage
from ...request import Request

logger = logging.getLogger(__name__)


class VkPostsCollector(AbstractCollector):
    STEP: int = 20
    _max_offset: int
    request_origin = None

    post_count = 0

    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            logger.debug('Start collecting posts')
            self.request_origin = self.get_request_origin(request)
            wall, has_posts = self._navigate_to_post_wall(request)

            if not has_posts:
                logger.debug('Wall has no posts: nothing to do')
                return

            self._max_offset = wall.get_max_offset()

            offset = 0
            try:
                new_posts = 0
                for offset in self.offset_generator(request, lambda: new_posts):
                    # resetting at each new offset
                    new_posts = self.process_posts_wall(request, wall, offset)

            except WsmcStopPostCollection:
                pass
            finally:
                VkPostStat.objects.update_or_create(**self.get_vk_post_stat_kwargs(request),
                                                    defaults={'last_offset': offset})

        return super().handle(request)

    def process_posts_wall(self, request: Request, wall: VkProfileWallPage, offset: int) -> int:
        new_count = 0
        post_item: SmPost = None

        def collect_posts_action():
            nonlocal new_count, post_item
            post_item = None

            for post_page_object in wall.collect_posts(offset):
                post_item = None

                post_dto = post_page_object.collect()
                # if SmPost.objects.filter(sm_post_id=post_dto.sm_post_id,
                #                          social_media=post_dto.social_media).exists():
                #     logger.info(f'Post already collected, skipping: {post_dto}')
                #     continue

                post_item, is_new = self.persist_post(post_dto, self.request_origin, request)

                likes_generator = post_page_object.collect_likes()
                if likes_generator:
                    for like in likes_generator:
                        self.persist_like(like, post_item, request)

                self.post_count += 1
                if is_new:
                    new_count += 1

        wall.retry_action(action=collect_posts_action,
                          on_fail=lambda: post_item.delete() if post_item else False,
                          additional_exceptions=[ElementNotInteractableException]
                          )

        if request.post_limit and self.post_count >= request.post_limit:
            raise WsmcStopPostCollection()

        return new_count

    @staticmethod
    def _navigate_to_post_wall(request: Request) -> Tuple[VkProfileWallPage, bool]:
        if request.is_group_request:
            wall: VkProfileWallPage = VkGroupPage(request.driver,
                                                  VkLinkBuilder.build_group(request.target_url)).go_to_wall()
        else:
            wall: VkProfileWallPage = VkProfilePage(request.driver,
                                                    VkLinkBuilder.build(request.target_url)).go_to_wall()

        has_posts = wall.wait_for_posts()
        return wall, has_posts

    def get_vk_post_stat_kwargs(self, request: Request):
        if request.is_group_request:
            return {'suspect_group': request.suspect_identity}
        return {'suspect_social_media', request.suspect_identity}

    def offset_generator(self, request: Request, new_amount_cb: Callable[[], int]) -> Generator[int, None, None]:
        last_offset: Optional[int] = None
        current_offset: int = 0

        try:
            post_stat = VkPostStat.objects.get(**self.get_vk_post_stat_kwargs(request))
            last_offset = post_stat.last_offset
        except VkPostStat.DoesNotExist:
            pass

        page = 0
        fwd_skipped = False

        def update_page_num():
            nonlocal page, current_offset
            page = int(current_offset / self.STEP)

        if not request.load_latest:
            logger.debug('Skipping newest posts')
            fwd_skipped = True
            if last_offset:
                current_offset = last_offset
            update_page_num()

        while current_offset <= self._max_offset:
            logger.debug(f'Generated offset: {current_offset}')
            yield current_offset
            new_posts = new_amount_cb()

            if not fwd_skipped and last_offset is not None and new_posts == 0:
                fwd_skipped = True
                current_offset = (page * self.STEP) + last_offset
                update_page_num()
            else:
                current_offset += self.STEP
                page += 1
