from typing import List, Tuple

from social_media.mimic.ok.flows.abstractokflow import AbstractOkFlow
from social_media.mimic.ok.requests.search.global_ import SearchGlobalRequest, SearchGlobalResponse, \
    SearchGlobalResponseBody
from social_media.mimic.ok.requests.search.locationsforfilter import SearchedLocation, SearchLocationsForFilterRequest, \
    SearchLocationsForFilterResponse
from social_media.mimic.ok.requests.users.getinfo import UsersGetInfoRequest, UsersGetInfoParams, UsersGetInfoResponse, \
    UsersGetInfoResponseBody
from social_media.mimic.ok.requests.users.getrelationinfo import UsersGetRelationInfoRequest, \
    UsersGetRelationInfoParams, UsersGetRelationInfoResponse, UsersGetRelationInfoResponseBody


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

    async def search_users_by_location(self,
                                       location: SearchedLocation,
                                       previous_anchor: str = None
                                       ) -> Tuple[
        SearchGlobalResponseBody, UsersGetRelationInfoResponseBody, UsersGetInfoResponseBody]:
        """
        Search users by location
        @param previous_anchor:
        @param location:
        @return:
        """
        search_request = SearchGlobalRequest(previous_anchor)
        search_request.add_filter(location.to_search_global_filter())

        relation_request = UsersGetRelationInfoRequest(
            params=UsersGetRelationInfoParams(fields='*'),
            supply_params=UsersGetRelationInfoParams(friend_ids=SearchGlobalRequest.EXECUTE_USER_ID_SUPPLY)
        )

        get_info_request = UsersGetInfoRequest(
            supply_params=UsersGetInfoParams(uids=SearchGlobalRequest.EXECUTE_USER_ID_SUPPLY)
        )

        batch_id = 'search.global'

        requests = [
            search_request,
            relation_request,
            get_info_request,
        ]

        response = await self.perform_multiple_requests(batch_id, requests)

        search_global_response: SearchGlobalResponse = response.find_response_by_request(search_request)
        relations_response: UsersGetRelationInfoResponse = response.find_response_by_request(relation_request)
        get_info_response: UsersGetInfoResponse = response.find_response_by_request(get_info_request)

        return search_global_response.get_body(), relations_response.get_body(), get_info_response.get_body()
