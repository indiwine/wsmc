import logging
from time import time
from typing import Generator, Optional, Callable, Tuple

from django.db import transaction
from selenium.common import ElementNotInteractableException, TimeoutException

from social_media.models import VkPostStat, SmPost, SmProfile
from social_media.social_media import SocialMediaEntities
from ..abstractcollector import AbstractCollector
from ...exceptions import WsmcStopPostCollection, WsmcWebDriverNativeApiCallTimout
from ...link_builders.vk import VkLinkBuilder
from ...options.vkoptions import VkOptions
from ...page_objects.vk.vkapipageobject import VkApiPageObject
from ...page_objects.vk.vkgrouppage import VkGroupPage
from ...page_objects.vk.vkpostpageobject import VkPostPageObject
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...page_objects.vk.vkprofilewallpage import VkProfileWallPage
from ...request import Request

logger = logging.getLogger(__name__)


class VkPostsCollector(AbstractCollector):
    _options: VkOptions = None
    _last_profile_collected_at: Optional[int] = None

    DELAY_BETWEEN_PROFILES = 60 * 3
    PROFILES_PER_REQUEST = 100 * 25
    STEP: int = 20
    request_origin = None
    post_count = 0

    def do_collect_profiles(self, request: Request):
        if self._last_profile_collected_at and (int(time()) - self._last_profile_collected_at) < self.DELAY_BETWEEN_PROFILES:
            logger.info('Skipping profile collection')
            return

        logger.info('Collecting profiles....')
        self._last_profile_collected_at = int(time())
        api_page_object = VkApiPageObject(request.driver, VkLinkBuilder.build_group(''))
        profiles = SmProfile.objects.select_for_update(skip_locked=True) \
                        .filter(was_collected=False, social_media=request.get_social_media_type) \
                        .values_list('oid', flat=True)[:self.PROFILES_PER_REQUEST]
        with transaction.atomic():
            if len(profiles) == 0:
                return

            try:
                for profile_dto_list in api_page_object.bulk_users_get(list(profiles)):
                    for profile_dto in profile_dto_list:
                        SmProfile.objects.filter(oid=profile_dto.oid, social_media=request.get_social_media_type) \
                            .update(was_collected=True, **self.as_dict_for_model(profile_dto))
                        profile = SmProfile.objects.get(oid=profile_dto.oid, social_media=request.get_social_media_type)

                        if profile.identify_location():
                            profile.save()
            except (TimeoutException, WsmcWebDriverNativeApiCallTimout) as e:
                self._last_profile_collected_at = int(time())
                logger.error(f'Collecting profiles - timeout', exc_info=e)

    def handle(self, request: Request):
        if request.can_process_entity(SocialMediaEntities.POSTS):
            logger.debug('Start collecting posts')
            self.request_origin = self.get_request_origin(request)
            wall, has_posts = self._navigate_to_post_wall(request)

            if not has_posts:
                logger.debug('Wall has no posts: nothing to do')
                return

            max_offset = wall.get_max_offset()

            offset = 0
            try:
                new_posts = 0
                for offset in self.offset_generator(request, lambda: new_posts, max_offset):
                    # resetting at each new offset
                    new_posts = self.process_posts_wall(request, wall, offset)
                    self._update_offset(request, offset)

            except WsmcStopPostCollection:
                pass
            finally:
                self._update_offset(request, offset)

        return super().handle(request)

    def _update_offset(self, request: Request, offset: int):
        try:
            VkPostStat.objects.update_or_create(**self.get_vk_post_stat_kwargs(request),
                                                defaults={'last_offset': offset})
        except Exception as e:
            logger.error('Cannot save VkPostStat object due to error', exc_info=e)

    def process_posts_wall(self, request: Request, wall: VkProfileWallPage, offset: int) -> int:
        new_count = 0

        def collect_posts_action() -> int:
            nonlocal new_count
            post_count = 0

            for post_page_object in wall.collect_posts(offset):
                post_count += 1

                post_dto = post_page_object.collect()

                if self._options.post_date_limit and post_dto.datetime < self._options.post_date_limit:
                    raise WsmcStopPostCollection('Post date limit reached')

                post_item, is_new = self.persist_post(post_dto, self.request_origin, request)

                self._parse_post_likes(post_page_object, post_item, request)

                if is_new:
                    new_count += 1
                self.do_collect_profiles(request)

            return post_count

        self.post_count += wall.retry_action(action=collect_posts_action,
                                             additional_exceptions=[ElementNotInteractableException]
                                             )
        request.mark_retry_successful()
        if self._options.post_count_limit and self.post_count >= self._options.post_count_limit:
            raise WsmcStopPostCollection(f'Post limit of {self._options.post_count_limit} reached')

        return new_count

    def _parse_post_likes(self,
                          post_page_object: VkPostPageObject,
                          post_item: SmPost,
                          request: Request
                          ):
        post_reactions_object = post_page_object.get_post_reactions_object()
        total_likes_count = post_reactions_object.likes_count()

        if total_likes_count == 0:
            return

        likes_in_db = self.count_likes(post_item)

        if likes_in_db == total_likes_count:
            return

        fan_box_object = post_reactions_object.open_likes_window()

        for like_authors in fan_box_object.generate_likes():
            _, new_likes_num = self.batch_persist_likes(like_authors, post_item, request)
            likes_in_db += new_likes_num

            if likes_in_db == total_likes_count:
                fan_box_object.close()
                break

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

    def offset_generator(self, request: Request, new_amount_cb: Callable[[], int], max_offset: int) -> Generator[
        int, None, None]:
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

        if not self._options.post_do_load_latest:
            logger.debug('Skipping newest posts')
            fwd_skipped = True
            if last_offset:
                current_offset = last_offset
            update_page_num()

        while current_offset <= max_offset:
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
