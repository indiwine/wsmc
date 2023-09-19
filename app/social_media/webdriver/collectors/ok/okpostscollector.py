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

        # Write properties for this collector and construct feed kwargs
        feed_kwargs = self.write_properties(request)

        # Initialize collector pipeline
        was_previous_anchor_jump = False
        current_anchor = None
        num_posts_collected = 0
        offset = 0
        previous_session_anchor, previous_session_offset = await self.try_find_anchor_from_db()

        try:

            # Main loop of this collector
            while True:
                offset += 1

                logger.debug(f'Fetching posts with offset {offset} and anchor {current_anchor}')

                total_fetched, new_post_count, current_anchor, can_continue = await self.posts_loop(feed_kwargs,
                                                                                                    request,
                                                                                                    current_anchor)
                num_posts_collected += total_fetched

                if not can_continue:
                    logger.info('No more posts available, stopping')
                    return

                # If post count limit is reached, let's stop
                if self.get_options().post_count_limit and num_posts_collected >= self.get_options().post_count_limit:
                    logger.info('Post count limit reached, stopping')
                    return

                # If no new posts present on page, and we have anchor from previous session, let jump to it
                if (was_previous_anchor_jump is False
                    and new_post_count == 0
                    and previous_session_anchor):

                    logger.info('No new posts, jumping to previous session anchor')
                    current_anchor = previous_session_anchor
                    offset += previous_session_offset
                    was_previous_anchor_jump = True

                # Maintain a healthy amount of delays between requests
                await self.random_await()
        finally:
            logger.info(f'Collected {num_posts_collected} posts')
            await self.write_anchor_to_db(current_anchor, offset)

    def write_properties(self, request: Request[OkRequestData]) -> dict:
        """
        Write properties for this collector and construct feed kwargs
        @param request:
        @return: feed kwargs
        """
        self.ok_stream = OkStreamFlow(request.data.client)
        self.request = request

        feed_kwargs = {}
        if request.is_group_request:
            feed_kwargs['gid'] = request.data.group_uid
            self.origin_entity = request.data.group_model
        else:
            feed_kwargs['uid'] = request.data.user_id
            self.origin_entity = request.data.profile_model

        return feed_kwargs

    async def posts_loop(self,
                         feed_kwargs: dict,
                         request: Request[OkRequestData],
                         current_anchor: str | None
                         ) -> Tuple[int, int, str, bool]:
        """
        Main loop for posts collection
        @param feed_kwargs:
        @param request:
        @param current_anchor:
        @return: total_posts, new_post_count, anchor, can_continue

        total_posts - number of posts received in a loop
        new_post_count - number of new posts received in a loop
        anchor - next anchor if it exists in the response or current_anchor if not (in case of no more posts)
        can_continue - True if we can continue, False otherwise (no more posts available or limit reached)
        """

        stream_response = await self.ok_stream.fetch_feed(**feed_kwargs, previous_anchor=current_anchor)
        stream_body = stream_response.get_body()

        total_posts = 0
        new_post_count = 0
        has_more = True

        if stream_body.anchor is None:
            logger.info('No anchor, we reached end of the feed. Stopping')
            has_more = False

        for post_dto, target_item in stream_body.post_generator():
            if self.get_options().post_date_limit and post_dto.datetime < self.get_options().post_date_limit:
                logger.info('Post date limit reached, stopping')
                has_more = False
                break

            # Persist post and its corresponding author, create new author if needed
            post, is_new = await self.apersist_post(post_dto, self.origin_entity, request)
            logger.debug(f'Post {"created" if is_new else "updated"}: {post_dto.datetime} ')

            total_posts += 1
            if is_new:
                new_post_count += 1

            if self.get_options().skip_likes_for_known_posts and not is_new:
                logger.debug('Skipping likes for known post')
                continue

            # Fetch and preserve likes for this post
            await self.collect_likes(post, target_item)

        can_continue = has_more and stream_body.available

        return total_posts, new_post_count, stream_body.anchor or current_anchor, can_continue

    async def try_find_anchor_from_db(self) -> Tuple[str | None, int | None]:
        """
        Try to find anchor from DB
        @return: anchor, offset
        """
        try:
            post_stat = await OkPostStat.objects.aget(**self.get_post_stat_kwargs())
            return post_stat.last_anchor, post_stat.last_offset
        except OkPostStat.DoesNotExist:
            return None, None

    async def write_anchor_to_db(self, current_anchor: str | None, offset: int):
        """
        Write anchor to DB

        Write occurs only if anchor is not None and offset is greater than offset in DB
        @param current_anchor:
        @param offset:
        @return:
        """
        if current_anchor:
            _, offset_in_db = await self.try_find_anchor_from_db()

            if offset_in_db is None or offset > offset_in_db:
                logger.debug(f'Writing anchor {current_anchor} to DB')

                await OkPostStat.objects.aupdate_or_create(
                    **self.get_post_stat_kwargs(),
                    defaults={
                        'last_offset': offset,
                        'last_anchor': current_anchor,
                    }
                )

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
