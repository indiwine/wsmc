import html
from datetime import datetime
from typing import Optional

from social_media.dtos import SmProfileDto, SmProfileMetadata
from social_media.webdriver.common import date_time_parse


class VkProfileNode:
    def __init__(self, raw_node: dict):
        self.raw_node = raw_node

    @property
    def name(self) -> str:
        result = f'{self.raw_node["first_name"]} {self.raw_node["last_name"]}'
        if 'maiden_name' in self.raw_node and self.raw_node['maiden_name']:
            result += f" ({self.raw_node['maiden_name']})"
        return html.unescape(result)

    def _get_prop_if_truthful(self, prop_name: str, unescape = True) -> Optional[any]:
        if prop_name in self.raw_node and self.raw_node[prop_name]:
            if unescape:
                return html.unescape(self.raw_node[prop_name])
            return self.raw_node[prop_name]

        return None

    @property
    def has_meta(self):
        return self.twitter or self.site

    @property
    def mobile_phone(self):
        return self._get_prop_if_truthful('mobile_phone')

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
        city_node = self._get_prop_if_truthful('city', False)
        if city_node:
            return html.unescape(city_node['title'])
        return None

    @property
    def country(self) -> Optional[str]:
        country_node = self._get_prop_if_truthful('country', False)
        if country_node:
            return html.unescape(country_node['title'])

        return None

    @property
    def education(self) -> Optional[str]:
        if 'universities' in self.raw_node and len(self.raw_node['universities']) > 0:
            university_node = self.raw_node['universities'][0]
            result = f'{university_node["name"]}'
            if 'faculty_name' in university_node:
                result += f' {university_node["faculty_name"]}'

            return html.unescape(result)
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
    
    def to_dto(self) -> SmProfileDto:
        dto = SmProfileDto(name=self.name,
                           location=self.location,
                           home_town=self.home_town,
                           university=self.education,
                           birthdate=self.birthday,
                           oid=self.oid,
                           country=self.country,
                           domain=self.domain
                           )
        metadata = None
        if self.has_meta:
            metadata = SmProfileMetadata(
                mobile_phone=self.mobile_phone,
                twitter=self.twitter,
                site=self.site
            )

        dto.metadata = metadata
        return dto
