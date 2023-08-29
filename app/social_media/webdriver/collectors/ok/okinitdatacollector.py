from social_media.mimic.ok.client import OkHttpClient
from social_media.mimic.ok.device import get_device
from social_media.webdriver import Request
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.collectors.abstractcollector import REQUEST_DATA
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkInitDataCollector(AbstractCollector[OkRequestData, OkOptions]):
    def handle(self, request: Request[REQUEST_DATA]):
        """
        Building new request data for OkRequestData
        @param request:
        @return:
        """

        request_data = OkRequestData()
        request_data.client = OkHttpClient(get_device())

        request.data = request_data
        return super().handle(request)
