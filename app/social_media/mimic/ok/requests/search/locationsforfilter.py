import dataclasses
from copy import copy
from typing import Optional, Type, List, Union

from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, OkRequestHttpMethod, \
    GenericResponse, GenericResponseBody, RESPONSE_BODY, AbstractResponse


@dataclasses.dataclass
class SearchLocationsForFilterParams(AbstractRequestParams):
    query: str


@dataclasses.dataclass
class SearchedLocation:
    countryId: int
    country: str
    city: str
    text: str
    city_id: int
    position: Optional[dict] = None


class SearchLocationsForFilterResponseBody(GenericResponseBody):
    locations: List[SearchedLocation]


class SearchLocationsForFilterResponse(GenericResponse[SearchLocationsForFilterResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return SearchLocationsForFilterResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        response = copy(raw_response)
        response['locations'] = [SearchedLocation(**location) for location in response['locations']]
        super().set_from_raw(response)


class SearchLocationsForFilterRequest(GenericRequest[SearchLocationsForFilterParams]):
    def __init__(self, query: str):
        super().__init__('search', 'locationsForFilter', params=SearchLocationsForFilterParams(query=query))

    @property
    def http_method(self) -> OkRequestHttpMethod:
        return OkRequestHttpMethod.GET

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return SearchLocationsForFilterResponse

