import asyncio
import logging
import random
from abc import ABC
from typing import List

from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.log_requests.mocking import load_from_storage
from social_media.mimic.ok.requests.abstractrequest import AbstractRequest
from social_media.mimic.ok.requests.executev2request import ExecuteV2Request, ExecuteV2Response

logger = logging.getLogger(__name__)


class AbstractOkFlow(ABC):
    """
    Abstract class for all OK flows
    """

    def __init__(self, client: OkHttpClient):
        self.client = client

    async def perform_batch_request(self, batch_id: str, request: AbstractRequest):
        """
        Create batch request with single request and run it

        Just a more convenient wrapper for perform_multiple_requests
        @param batch_id:
        @param request:
        @return: Response for request given
        """
        response: ExecuteV2Response = await self.perform_multiple_requests(batch_id, [request])
        return response.find_response_by_request(request)

    async def perform_multiple_requests(self, batch_id: str, requests: List[AbstractRequest]) -> ExecuteV2Response:
        """
        Create batch request with multiple requests and run it
        @param batch_id:
        @param requests:
        @return: Response for all requests given
        """
        batch_request = ExecuteV2Request(batch_id)
        for request in requests:
            batch_request.append(request)
        response: ExecuteV2Response = await self.client.make(batch_request)
        return response

    async def run_requests_from_a_file(self, sub_path: str, min_delay: int = 1, max_delay: int = 10):
        """
        Run requests from a file
        @param sub_path:
        @param min_delay:
        @param max_delay:
        @return:
        """
        for log_request in load_from_storage(sub_path):
            # A little bit of a delay to simulate real user
            random_int = random.randint(min_delay, max_delay)
            logger.debug(f'Waiting for {random_int} seconds')
            await asyncio.sleep(random_int)

            await self.client.make(log_request)
