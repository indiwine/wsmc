from datetime import datetime
from typing import Optional

from social_media.webdriver.common import date_time_parse


class VkProfileNode:
    def __init__(self, raw_node: dict):
        self.raw_node = raw_node

    @property
    def name(self) -> str:
        result = f'{self.raw_node["first_name"]} {self.raw_node["last_name"]}'
        if 'maiden_name' in self.raw_node and self.raw_node['maiden_name']:
            result += f" ({self.raw_node['maiden_name']})"
        return result

    def _get_prop_if_truthful(self, prop_name: str) -> Optional[any]:
        if prop_name in self.raw_node and self.raw_node[prop_name]:
            return self.raw_node[prop_name]

        return None

    @property
    def has_meta(self):
        return self.tv or self.twitter or self.site

    @property
    def tv(self):
        return self._get_prop_if_truthful('tv')

    @property
    def twitter(self):
        return self._get_prop_if_truthful('twitter')

    @property
    def site(self):
        return self._get_prop_if_truthful('site')

    @property
    def domain(self):
        return self._get_prop_if_truthful('domain')

    @property
    def home_town(self) -> Optional[str]:
        return self._get_prop_if_truthful('home_town')

    @property
    def location(self) -> Optional[str]:
        city_node = self._get_prop_if_truthful('city')
        if city_node:
            return city_node['title']
        return None

    @property
    def country(self) -> Optional[str]:
        country_node = self._get_prop_if_truthful('country')
        if country_node:
            return country_node['title']

        return None

    @property
    def education(self) -> Optional[str]:
        if 'universities' in self.raw_node and len(self.raw_node['universities']) > 0:
            university_node = self.raw_node['universities'][0]
            result = f'{university_node["name"]}'
            if 'faculty_name' in university_node:
                result += f' {university_node["faculty_name"]}'

            return result
        return None

    @property
    def birthday(self) -> Optional[datetime]:
        bdate = self._get_prop_if_truthful('bdate')
        if bdate:
            return date_time_parse(bdate)
        return None

    @property
    def oid(self) -> str:
        return str(self.raw_node['id'])
