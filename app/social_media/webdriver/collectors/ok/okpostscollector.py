import logging
from typing import Tuple, Union

from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.models import SmPost, OkPostStat, SmGroup, SmProfile
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)


class OkPostsCollector(AbstractCollector[OkRequestData, OkOptions]):
    ok_stream: OkStreamFlow
    request: Request[OkRequestData]
    origin_entity: Union[SmGroup, SmProfile]

    async def handle(self, request: Request[OkRequestData]):
        assert request.data.group_uid is not None or request.data.user_id is not None, 'Group UID or User ID must be present'


        feed_kwargs = {}
        if request.is_group_request:
            feed_kwargs['gid'] = request.data.group_uid
            self.origin_entity = request.data.group_model
        else:
            feed_kwargs['uid'] = request.data.user_id
            self.origin_entity = request.data.profile_model

        logger.debug(f'Collecting posts for {"group" if request.is_group_request else "profile"}: {feed_kwargs}')
        self.ok_stream = OkStreamFlow(request.data.client)
        self.request = request

        previous_session_anchor, _ = await self.try_find_anchor_from_db()
        was_previous_anchor_jump = False

        previous_anchor = None


        num_posts_collected = 0
        offset = 0

        try:
            while True:
                # Fetch posts
                stream_response = await self.ok_stream.fetch_feed(**feed_kwargs,
                                                                  previous_anchor=previous_anchor)
                # Extract posts from response
                stream_body = stream_response.get_body()
                # Save anchor for next request
                previous_anchor = stream_body.anchor

                if not stream_body.available:
                    logger.info('No more posts available, stopping')
                    break

                new_post_count = 0

                # Iterate over posts
                for post_dto, target_item in stream_body.post_generator():

                    num_posts_collected += 1

                    # Persist post and its corresponding author, create new author if needed
                    post, is_new = await self.apersist_post(post_dto, self.origin_entity, request)
                    logger.debug(f'Post {"created" if is_new else "updated"}: {post_dto} ')

                    if is_new:
                        new_post_count += 1

                    if self.get_options().skip_likes_for_known_posts and not is_new:
                        logger.debug('Skipping likes for known post')
                        continue

                    # Fetch and preserve likes for this post
                    await self.collect_likes(post, target_item)

                    # A little bit of heuristic to stop collecting posts
                    if self.get_options().post_date_limit and post_dto.datetime < self.get_options().post_date_limit:
                        logger.info('Post date limit reached, stopping')
                        return

                # If no new posts present on page and we have anchor from previous session, let jump to it
                if not was_previous_anchor_jump and new_post_count == 0 and previous_session_anchor:
                    logger.info('No new posts, jumping to previous session anchor')
                    previous_anchor = previous_session_anchor
                    was_previous_anchor_jump = True
                    continue

                offset += 1
                if self.get_options().post_count_limit and num_posts_collected >= self.get_options().post_count_limit:
                    logger.info('Post count limit reached, stopping')
                    return

                # Maintain a healthy amount of delays between requests
                await self.random_await()
        finally:
            logger.info(f'Collected {num_posts_collected} posts')
            if previous_anchor:
                _, offset_in_db = await self.try_find_anchor_from_db()

                if offset_in_db is None or offset > offset_in_db:
                    await OkPostStat.objects.aupdate_or_create(
                        **self.get_post_stat_kwargs(),
                        defaults={
                            'last_offset': offset,
                            'last_anchor': previous_anchor,
                        }
                    )

    async def try_find_anchor_from_db(self) -> Tuple[str | None, int | None]:
        """
        Try to find anchor from DB
        @return:
        """
        try:
            post_stat = await OkPostStat.objects.aget(**self.get_post_stat_kwargs())
            return post_stat.last_anchor, post_stat.last_offset
        except OkPostStat.DoesNotExist:
            return None, None

    async def collect_likes(self, post_item: SmPost, target_item: BaseFeedEntity):
        """
        Collect likes for a single post
        @param post_item:
        @param target_item:
        @return:
        """
        logger.debug(f'Collecting likes for post {post_item}')

        like_summary = target_item.extract_like_summary()

        # Not all posts have likes functionality enabled
        if like_summary is None:
            logger.debug('No like summary, skipping')
            return

        total_likes_count = like_summary.count
        if total_likes_count == 0:
            logger.debug('No likes, skipping')
            return

        likes_in_db = await self.acount_likes(post_item)
        if likes_in_db >= total_likes_count:
            logger.debug('All likes already collected, skipping')
            return

        like_id = like_summary.like_id

        previous_anchor = None
        likes_processed = 0

        # Start looping through likes
        while True:

            logger.debug(f'Fetching likes for post {post_item.id} with anchor {previous_anchor}')
            likes_response = await self.ok_stream.fetch_likes(like_id, previous_anchor)
            likes_body = likes_response.get_body()

            # Persist likes and its corresponding authors, create new authors if needed
            authors = likes_body.to_author_dtos()
            likes_processed += len(authors)
            _, new_likes_num = await self.abatch_persist_likes(authors, post_item, self.request)

            # While here, we can update authors profiles, since OK provides us with the full info
            profile_dtos = likes_body.to_profile_dtos()
            await self.aupdate_collected_profiles(profile_dtos, self.request)

            # A little bit of heuristic to stop collecting likes
            likes_in_db += new_likes_num
            if likes_in_db >= total_likes_count:
                logger.info('All likes collected')
                return

            previous_anchor = likes_body.anchor
            if not likes_body.has_more:
                logger.info('No more likes available, stopping')
                return

            if likes_processed >= total_likes_count:
                logger.info('All likes processed, stopping')
                return

            # Maintain a healthy amount of delays between requests
            await self.random_await(max_delay=15)

    def get_post_stat_kwargs(self):
        return {
            'suspect_group' if self.request.is_group_request else 'suspect_social_media': self.request.suspect_identity
        }
