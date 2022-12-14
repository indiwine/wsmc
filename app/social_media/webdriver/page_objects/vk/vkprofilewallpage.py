import logging
import urllib.parse
from typing import Generator

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from .abstractvkpageobject import AbstractVkPageObject
from .vkpostpageobject import VkPostPageObject

logger = logging.getLogger(__name__)


class VkProfileWallPage(AbstractVkPageObject):

    def posts(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '#page_wall_posts > .post')

    def last_page_link(self):
        return self.driver.find_element(By.CSS_SELECTOR, '#fw_pages > a.pg_lnk:last-child')

    def wait_for_posts(self):
        self.get_wait().until(EC.presence_of_element_located((By.ID, 'page_wall_posts')))

    def collect_posts(self, offset: int) -> Generator[SmPostDto, None, None]:
        logger.debug(f'Collecting posts for offset: {offset}')
        self.clear_requests()
        self.navigate_to(self.link_strategy.add_offset(self.driver.current_url, offset))
        self.wait_for_posts()

        for post_node in self.posts():
            yield VkPostPageObject(self.driver, self.link_strategy, post_node).collect()

    def get_max_offset(self) -> int:
        parse_result = urllib.parse.urlparse(self.last_page_link().get_attribute('href'))
        params = urllib.parse.parse_qs(parse_result[4])
        return int(params['offset'][0])
