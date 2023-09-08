import logging

from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.models import SmPost, OkPostStat
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)


class OkGroupPostsCollector(AbstractCollector[OkRequestData, OkOptions]):
    ok_stream: OkStreamFlow
    request: Request[OkRequestData]

    async def handle(self, request: Request[OkRequestData]):
        if request.data.group_uid is None:
            raise ValueError('Group UID must be present')

        logger.debug(f'Collecting posts for group {request.data.group_uid}')
        self.ok_stream = OkStreamFlow(request.data.client)
        self.request = request

        previous_session_anchor = await self.try_find_anchor_from_db(request)

        previous_anchor = None
        num_posts_collected = 0
        offset = 0
        try:
            while True:
                # Fetch posts
                stream_response = await self.ok_stream.fetch_feed(request.data.group_uid, previous_anchor)
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
                    post, is_new = await self.apersist_post(post_dto, request.data.group_model, request)
                    logger.debug(f'Post {"created" if is_new else "updated"}: {post_dto} ')

                    if is_new:
                        new_post_count += 1

                    # Fetch and preserve likes for this post
                    await self.collect_likes(post, target_item)

                    # A little bit of heuristic to stop collecting posts
                    if self.get_options().post_date_limit and post_dto.datetime < self.get_options().post_date_limit:
                        logger.info('Post date limit reached, stopping')
                        return

                # If no new posts present on page and we have anchor from previous session, let jump to it
                if new_post_count == 0 and previous_session_anchor:
                    logger.info('No new posts, jumping to previous session anchor')
                    previous_anchor = previous_session_anchor
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
                await OkPostStat.objects.aupdate_or_create(
                    suspect_group=request.suspect_identity,
                    defaults={
                        'last_offset': offset,
                        'last_anchor': previous_anchor,
                    }
                )

    async def try_find_anchor_from_db(self, request: Request[OkRequestData]) -> str:
        """
        Try to find anchor from DB
        @param request:
        @return:
        """
        try:
            post_stat = await OkPostStat.objects.aget(suspect_group=request.suspect_identity)
            return post_stat.last_anchor
        except OkPostStat.DoesNotExist:
            return None

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
