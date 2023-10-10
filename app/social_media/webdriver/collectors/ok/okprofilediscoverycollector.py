from social_media.mimic.ok.flows.okcommonflow import OkCommonFlow
from social_media.mimic.ok.flows.oksearchflow import OkSearchFlow
from social_media.mimic.ok.requests.search.locationsforfilter import SearchedLocation
from social_media.models import SuspectPlace
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData


class OkProfileDiscoveryCollector(AbstractCollector[OkRequestData, OkOptions]):

    common_flow: OkCommonFlow
    search_flow: OkSearchFlow

    async def handle(self, request: Request):
        """
        Collector discovers profiles (i.e. using search) and saves them to the database for further processing
        @param request:
        @return:
        """
        assert request.is_place_request, 'Request must be a place request'


        self.common_flow = OkCommonFlow(request.data.client)
        self.search_flow = OkSearchFlow(request.data.client)


        # Main loop of the collector
        while True:
            pass


    async def determine_location(self, place: SuspectPlace) -> SearchedLocation:
        """
        Determine location of the profile
        @param place:
        @raise RuntimeError: if cannot find any relevant locations for place
        @return:
        """

        # Find relevant locations
        places = await self.search_flow.search_locations_for_filter(place.__str__())

        if len(places) == 0:
            raise RuntimeError(f'Cannot find any relevant locations for place: {place}')

        # Return first location, typically it is the most relevant one
        return places[0]

