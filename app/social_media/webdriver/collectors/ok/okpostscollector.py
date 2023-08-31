import logging

from social_media.mimic.ok.flows.okstreamflow import OkStreamFlow
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


logger = logging.getLogger(__name__)

class OkPostsCollector(AbstractCollector[OkRequestData, OkOptions]):
    ok_stream: OkStreamFlow
    async def handle(self, request: Request[OkRequestData]):
        if request.data.group_uid is None:
            raise ValueError('Group UID must be present')

        logger.debug(f'Collecting posts for group {request.data.group_uid}')
        self.ok_stream = OkStreamFlow(request.data.client)

        previous_anchor = None
        while True:
            stream_response = await self.ok_stream.fetch_feed(request.data.group_uid, previous_anchor)
            stream_body = stream_response.get_body()
            if not stream_body.available:
                logger.info('No more posts available, stopping')
                break

            for post, target_item in stream_body.post_generator():
                post, is_new = await self.apersist_post(post, request, request.suspect_identity)


    async def collect_likes(self):
        pass
