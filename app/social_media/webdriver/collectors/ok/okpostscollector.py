import logging
from typing import Tuple, Union, Optional

from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.models import SmPost, SmGroup, SmProfile
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.collectors.ok.okmainloopmixin import OkMainLoopMixin
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)


class OkPostsCollector(AbstractCollector[OkRequestData, OkOptions], OkMainLoopMixin):
    ok_stream: OkStreamFlow
    request: Request[OkRequestData]
    origin_entity: Union[SmGroup, SmProfile]
    feed_kwargs: dict
    num_posts_collected: int
    new_post_count: int

    async def fetch_data(self, request: Request[OkRequestData], previous_anchor: Optional[str]) -> Tuple[str, bool]:
        total_fetched, self.new_post_count, current_anchor, can_continue = await self.posts_loop(self.feed_kwargs,
                                                                                                 request,
                                                                                                 previous_anchor)
        self.num_posts_collected += total_fetched

        post_limit_reached = (self.get_options().post_count_limit and
                              self.num_posts_collected >= self.get_options().post_count_limit)

        continue_loop = can_continue and not post_limit_reached
        if continue_loop:
            await self.random_await()

        return current_anchor, continue_loop

    async def can_jump_to_previous_anchor(self) -> bool:
        return self.new_post_count == 0

    async def handle(self, request: Request[OkRequestData]):
        assert request.data.group_uid is not None or request.data.user_id is not None, 'Group UID or User ID must be present'

        # Write properties for this collector and construct feed kwargs
        self.write_properties(request)
        await self.main_loop(request)

    def write_properties(self, request: Request[OkRequestData]) -> dict:
        """
        Write properties for this collector and construct feed kwargs
        @param request:
        @return: feed kwargs
        """
        self.num_posts_collected = 0
        self.new_post_count = 0
        self.ok_stream = OkStreamFlow(request.data.client)
        self.request = request

        feed_kwargs = {}
        if request.is_group_request:
            feed_kwargs['gid'] = request.data.group_uid
            self.origin_entity = request.data.group_model
        else:
            feed_kwargs['uid'] = request.data.user_id
            self.origin_entity = request.data.profile_model

        self.feed_kwargs = feed_kwargs

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
