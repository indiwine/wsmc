import logging
import urllib.parse
from typing import Generator

from selenium.common import NoSuchElementException
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

    @staticmethod
    def page_wall_posts_locator():
        return By.ID, 'page_wall_posts'

    @staticmethod
    def message_page_locator():
        return By.CLASS_NAME, 'message_page'

    def wait_for_posts(self) -> bool:

        self.get_wait().until(
            EC.any_of(
                EC.presence_of_element_located(self.page_wall_posts_locator()),
                EC.presence_of_element_located(self.message_page_locator())
            )
        )

        try:
            self.driver.find_element(*self.page_wall_posts_locator())
            return True
        except NoSuchElementException:
            return False

    def collect_posts(self, offset: int) -> Generator[VkPostPageObject, None, None]:
        logger.debug(f'Collecting posts for offset: {offset}')
        self.clear_requests()
        self.navigate_to(self.link_strategy.add_offset(self.driver.current_url, offset))
        logger.debug('Navigation done. Waiting for posts to appear.')
        has_posts = self.wait_for_posts()

        if not has_posts:
            logger.debug('No posts on page present!')
            return

        for post_node in self.posts():
            yield VkPostPageObject(self.driver, self.link_strategy, post_node)

    def get_max_offset(self) -> int:
        parse_result = urllib.parse.urlparse(self.last_page_link().get_attribute('href'))
        params = urllib.parse.parse_qs(parse_result[4])
        return int(params['offset'][0])
