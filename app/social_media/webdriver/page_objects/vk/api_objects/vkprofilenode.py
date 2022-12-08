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

    @property
    def home_town(self) -> Optional[str]:
        if 'home_town' in self.raw_node:
            return self.raw_node['home_town']
        return None

    @property
    def location(self) -> Optional[str]:
        if 'city' in self.raw_node:
            result = self.raw_node['city']['title']
            if 'country' in self.raw_node:
                result += f", {self.raw_node['country']['title']}"
            return result
        return None

    @property
    def education(self) -> Optional[str]:
        if 'universities' in self.raw_node and len(self.raw_node['universities']) > 0:
            university_node = self.raw_node['universities'][0]
            return f'{university_node["name"]} {university_node["faculty_name"]}'
        return None

    @property
    def birthday(self) -> Optional[datetime]:
        if 'bdate' in self.raw_node:
            return date_time_parse(self.raw_node['bdate'])
        return None
