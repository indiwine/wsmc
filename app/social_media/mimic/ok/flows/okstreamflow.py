from typing import Optional

from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.like.getinfo import LikeGetInfoResponse, LikeGetInfoRequest
from social_media.mimic.ok.requests.stream.get import StreamGetResponse, StreamGetRequest


class OkStreamFlow(AbstractOkFlow):
    """
    Ok stream flow for feed-related requests
    """

    async def fetch_feed(self, gid: str, previous_anchor: Optional[str] = None) -> StreamGetResponse:
        """
        Fetch feed for group by group UID
        @param gid:
        @param previous_anchor:
        @return:
        """
        batch_id = 'stream.get-first' if not previous_anchor else 'stream.get-more'

        stream_get_request = StreamGetRequest(gid)
        stream_get_response: StreamGetResponse = await self.perform_batch_request(
            batch_id,
            stream_get_request
        )

        return stream_get_response


    async def fetch_likes(self, like_id: str, previous_anchor: Optional[str] = None) -> LikeGetInfoResponse:
        """
        Fetch likes for post by like_id
        @param previous_anchor:
        @param like_id:
        @return:
        """
        batch_id = 'like.getInfo'

        like_get_info_request = LikeGetInfoRequest(like_id, previous_anchor)
        like_get_info_response: LikeGetInfoResponse = await self.perform_batch_request(
            batch_id,
            like_get_info_request
        )

        return like_get_info_response

