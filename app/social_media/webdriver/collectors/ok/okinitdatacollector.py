from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.device import get_random_device, default_device
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkInitDataCollector(AbstractCollector[OkRequestData, OkOptions]):
    async def handle(self, request: Request[OkRequestData]):
        """
        Building new request data for OkRequestData
        @param request:
        @return:
        """

        request_data = OkRequestData()
        # We initialize the client without a device, we will set it later
        request_data.client = OkHttpClient()

        request.data = request_data
