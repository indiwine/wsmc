import re

from selenium.webdriver.common.by import By

from social_media.dtos import SmGroupDto
from .abstractvkpageobject import AbstractVkPageObject
from .vkprofilewallpage import VkProfileWallPage
from ...exceptions import WsmcWebDriverGroupException


class VkGroupPage(AbstractVkPageObject):

    def meta_title(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')

    def meta_url(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:url"]')

    def permalink(self) -> str:
        return self.meta_url().get_attribute('content')

    def profile_wall_link(self):
        return self.driver.find_element(By.CSS_SELECTOR, '.page_block ._wall_tab_own a')

    def go_to_group(self):
        self.navigate_to(self.link_strategy.get_profile_link())

    def collect_group(self) -> SmGroupDto:
        self.go_to_group()
        return SmGroupDto(
            permalink=self.permalink(),
            name=self.meta_title().get_attribute('content'),
            oid=self._extract_id()
        )

    def go_to_wall(self):
        self.navigate_to(self.profile_wall_link().get_attribute('href'))
        return VkProfileWallPage(self.driver, self.link_strategy)

    def _extract_id(self) -> str:
        pattern = re.compile(r"\/public(?P<oid>\d+)")
        match = pattern.search(self.permalink())
        if match is None:
            raise WsmcWebDriverGroupException(f'Cannot locate "/public" in url: "{self.permalink()}"')

        return match.group('oid')
