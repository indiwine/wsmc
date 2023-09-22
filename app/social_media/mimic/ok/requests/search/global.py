import dataclasses
import json
from typing import List

from dataclasses_json import dataclass_json

from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams


@dataclasses.dataclass
class SearchGlobalFilter:
    city: str
    country_ids: List[int]
    type: str = 'user'

@dataclasses.dataclass
class SearchGlobalRequestParams(AbstractRequestParams):
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
        result['filters'] = json.dumps(result['filters'])
        result['queryMeta'] = json.dumps(result['queryMeta'])
        return result
