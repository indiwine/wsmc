import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import SmGroupDto
from social_media.social_media import SocialMediaTypes
from .abstractvkpageobject import AbstractVkPageObject
from .vkprofilewallpage import VkProfileWallPage
from ...exceptions import WsmcWebDriverGroupException, WsmcWebDriverGroupNotFoundException


class VkGroupPage(AbstractVkPageObject):

    def meta_title(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')

    def meta_url(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:url"]')

    def permalink(self) -> str:
        return self.meta_url().get_attribute('content')

    @staticmethod
    def group_cover_locator():
        return By.CLASS_NAME, 'redesigned-group-cover'

    @staticmethod
    def group_blocked_locator():
        return By.CLASS_NAME, 'groups_blocked'

    def profile_wall_link(self):
        return self.driver.find_element(By.CSS_SELECTOR, '.page_block ._wall_tab_own a')

    def go_to_group(self):
        url = self.link_strategy.get_group_link()
        if self.driver.current_url != url:
            self.navigate_to(url)

    def collect_group(self) -> SmGroupDto:
        self.go_to_group()

        self.get_wait().until(EC.any_of(
            EC.presence_of_element_located(self.group_cover_locator()),
            EC.title_is(self.NOT_FOUND_TITLE),
            EC.presence_of_element_located(self.group_blocked_locator())
        ))

        if self.is_404() or self.driver.find_element_safe(*self.group_blocked_locator()):
            raise WsmcWebDriverGroupNotFoundException(
                f'Group cannot be found or blocked at "{self.driver.get_current_url_safe}"')

        return SmGroupDto(
            permalink=self.permalink(),
            name=self.meta_title().get_attribute('content'),
            oid=self._extract_id(),
            social_media=SocialMediaTypes.VK
        )

    def go_to_wall(self):
        self.go_to_group()
        self.navigate_to(self.profile_wall_link().get_attribute('href'))
        return VkProfileWallPage(self.driver, self.link_strategy)

    def _extract_id(self) -> str:
        pattern = re.compile(r"\/(?:public|club)(?P<oid>\d+)")
        match = pattern.search(self.permalink())
        if match is None:
            raise WsmcWebDriverGroupException(f'Cannot locate group ID in url: "{self.permalink()}"')

        return match.group('oid')
