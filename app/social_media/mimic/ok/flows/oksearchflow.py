from typing import List

from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.search.locationsforfilter import SearchedLocation, SearchLocationsForFilterRequest, \
    SearchLocationsForFilterResponse


class OkSearchFlow(AbstractOkFlow):
    async def search_locations_for_filter(self, query: str) -> List[SearchedLocation]:
        """
        Search locations for filter
        @param query:
        @return:
        """
        search_locations_request = SearchLocationsForFilterRequest(query)
        search_result: SearchLocationsForFilterResponse = await self.client.make(request=search_locations_request)
        return search_result.get_body().locations


    async def search_users_by_location(self, location: SearchedLocation):
        """
        Search users by location
        @param location:
        @return:
        """
        search_filter = location.to_search_global_filter()
        batch_id = 'search.global'
        batech_request = ExecuteV2Request(batch_id)

