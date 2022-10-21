from datetime import datetime
from typing import Optional

import dateparser


class VkProfileNode:
    def __init__(self, raw_node: dict):
        self.raw_node = raw_node

    @property
    def name(self) -> str:
        return f'{self.raw_node["first_name"]} {self.raw_node["last_name"]}'

    @property
    def home_town(self) -> Optional[str]:
        if 'home_town' in self.raw_node:
            return self.raw_node['home_town']
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
            return dateparser.parse(self.raw_node['bdate'])
        return None
