import logging

from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.models import SmPost
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

        previous_anchor = None
        num_posts_collected = 0
        while True:
            stream_response = await self.ok_stream.fetch_feed(request.data.group_uid, previous_anchor)
            stream_body = stream_response.get_body()
            if not stream_body.available:
                logger.info('No more posts available, stopping')
                break

            for post_dto, target_item in stream_body.post_generator():
                num_posts_collected += 1
                post, is_new = await self.apersist_post(post_dto, request.data.group_model, request)
                await self.collect_likes(post, target_item)

            if self.get_options().post_count_limit and num_posts_collected >= self.get_options().post_count_limit:
                logger.info('Post count limit reached, stopping')
                break

            # Maintain a healthy amount of delays between requests
            await self.random_await()


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
        like_id = like_summary.like_id

        previous_anchor = None

        # Start looping through likes
        while True:

            likes_response = await self.ok_stream.fetch_likes(like_id, previous_anchor)
            likes_body = likes_response.get_body()

            # Persist likes and its corresponding authors, create new authors if needed
            authors = likes_body.to_author_dtos()
            _, new_likes_num = await self.abatch_persist_likes(authors, post_item, self.request)

            # While here, we can update authors profiles, since OK provides us with the full info
            profile_dtos = likes_body.to_profile_dtos()
            await self.aupdate_collected_profiles(profile_dtos, self.request)


            # A little bit of heuristic to stop collecting likes
            likes_in_db += new_likes_num
            if likes_in_db >= total_likes_count:
                logger.info('All likes collected')
                break

            previous_anchor = likes_body.anchor
            if not likes_body.has_more:
                logger.info('No more likes available, stopping')
                break

            # Maintain a healthy amount of delays between requests
            await self.random_await()
