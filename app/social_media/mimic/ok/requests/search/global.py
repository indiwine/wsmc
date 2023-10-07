import dataclasses
from typing import List, Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, GenericResponseBody, \
    GenericResponse
from social_media.mimic.ok.requests.common import to_json_slim
from social_media.mimic.ok.requests.entities.user import UserItem


@dataclasses.dataclass
class SearchGlobalFilter:
    city: str
    country_ids: List[int]
    type: str = 'user'


@dataclasses.dataclass
class SearchGlobalParams(AbstractRequestParams):
    count: int = 40
    fieldset: str = 'android.5'
    related_types: str = 'USER,GROUP,COMMUNITY,VIDEO,APP,MUSIC,CONTENT'
    screen: str = 'GLOBAL_SEARCH_USERS'
    types: str = 'USER'
    filters: List[SearchGlobalFilter] = dataclasses.field(default_factory=lambda: [])
    queryMeta: dict = dataclasses.field(default_factory=lambda: {"sourceLocation": "DISCOVERY_SEARCH"})

    def add_filter(self, search_fileter: SearchGlobalFilter):
        self.filters.append(search_fileter)

    def add_filter_by_city(self, city: str, country_id: int):
        self.add_filter(SearchGlobalFilter(city=city, country_ids=[country_id]))

    def to_execute_dict(self) -> dict:
        result = super().to_execute_dict()
        result['filters'] = to_json_slim(result['filters'])
        result['queryMeta'] = to_json_slim(result['queryMeta'])
        return result


@dataclasses.dataclass
class SearchFoundItem:
    item_type: str
    entity_ref: str
    type: str
    type_msg: str
    type_qualifier: str
    text: str
    scope: str


@nested_dataclass
class SearchGlobalEntities:
    users: List[UserItem]


class SearchGlobalResponseBody(GenericResponseBody):
    qid: str
    context: str
    found: list
    entities: list
    has_more: bool
    totalCount: int
    anchor: Optional[str] = None


class SearchGlobalResponse(GenericResponse[SearchGlobalResponseBody]):
    @staticmethod
    def get_body_class():
        return SearchGlobalResponseBody

    def set_from_raw(self, raw_response: dict):
        response = raw_response.copy()
        response['entities'] = SearchGlobalEntities(**response['entities'])
        super().set_from_raw(response)


class SearchGlobalRequest(GenericRequest[SearchGlobalParams, None]):
    def __init__(self):
        super().__init__('search', 'global', params=SearchGlobalParams())

    def add_filter_by_city(self, city: str, country_id: int):
        self.params.add_filter_by_city(city, country_id)

    @staticmethod
    def bound_response_cls():
        return SearchGlobalResponse
