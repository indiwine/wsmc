import logging
from typing import Tuple, List, Optional

from social_media.mimic.ok.flows.okcommonflow import OkCommonFlow
from social_media.mimic.ok.flows.oksearchflow import OkSearchFlow
from social_media.mimic.ok.requests.entities.user import UserItem
from social_media.mimic.ok.requests.search.locationsforfilter import SearchedLocation
from social_media.models import SuspectPlace, SmProfile, Suspect, SuspectSocialMediaAccount
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.collectors.ok.okmainloopmixin import OkMainLoopMixin
from social_media.webdriver.options.okoptions import OkOptions
from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)


class OkProfileDiscoveryCollector(AbstractCollector[OkRequestData, OkOptions], OkMainLoopMixin):
    request: Request[OkRequestData]
    common_flow: OkCommonFlow
    search_flow: OkSearchFlow
    picked_location: SearchedLocation

    num_of_new_profiles: int
    num_of_profiles: int

    async def handle(self, request: Request[OkRequestData]):
        """
        Collector discovers profiles (i.e. using search) and saves them to the database for further processing
        @param request:
        @return:
        """
        assert request.is_place_request, 'Request must be a place request'

        self.request = request
        self.num_of_profiles = 0
        self.common_flow = OkCommonFlow(request.data.client)
        self.search_flow = OkSearchFlow(request.data.client)

        self.picked_location = await self.determine_location(request.suspect_identity)

        await self.main_loop(request)

    async def fetch_data(self,
                         request: Request[OkRequestData],
                         previous_anchor: Optional[str]
                         ) -> Tuple[str | None, bool]:
        anchor, has_more, users = await self.discover_profiles(self.picked_location, previous_anchor)
        if has_more:
            await self.random_await()
        return anchor, has_more

    async def can_jump_to_previous_anchor(self) -> bool:
        return self.num_of_new_profiles == 0

    async def discover_profiles(self,
                                location: SearchedLocation,
                                previous_anchor: Optional[str] = None
                                ) -> Tuple[str, bool, List[UserItem]]:
        """
        Discover profiles for location
        @param location:
        @param previous_anchor:
        @return: anchor, has_more, users
        """
        search_info, _, users = await self.search_flow.search_users_by_location(location, previous_anchor)
        self.num_of_new_profiles = 0
        for user in users.users:
            self.num_of_profiles += 1
            user_dto = user.to_profile_dto()
            profile, is_new = await SmProfile.objects.aget_or_create(oid=user_dto.oid,
                                                                     social_media=self.request.get_social_media_type,
                                                                     defaults={
                                                                         **self.as_dict_for_model(user_dto),
                                                                         'credentials': self.request.credentials,
                                                                         'social_media': self.request.get_social_media_type,
                                                                     })

            if is_new and user.has_url:
                logger.info(f'New profile discovered: {profile}')
                suspect = await Suspect.objects.acreate(name=user_dto.name)
                sm_account = await SuspectSocialMediaAccount.objects.acreate(
                    link=user_dto.metadata.permalink,
                    credentials=self.request.credentials,
                    suspect=suspect
                )
                self.num_of_new_profiles += 1
                await self.aresolve_and_save_profile(profile, user_dto)

        if self.get_options().discover_profiles_limit and self.num_of_profiles >= self.get_options().discover_profiles_limit:
            return search_info.anchor, False, users.users

        return search_info.anchor, search_info.has_more, users.users

    async def determine_location(self, place: SuspectPlace) -> SearchedLocation:
        """
        Determine location of the profile
        @param place:
        @raise RuntimeError: if it cannot find any relevant locations for place
        @return:
        """

        # Find relevant locations
        places = await self.search_flow.search_locations_for_filter(place.__str__())

        if len(places) == 0:
            raise RuntimeError(f'Cannot find any relevant locations for place: {place}')

        # Return first location, typically it is the most relevant one
        return places[0]
