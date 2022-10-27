import logging
from typing import Generator

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from .abstractokpageobject import AbstractOkPageObject
from .oksinglepostpage import OkSinglePostPage

logger = logging.getLogger(__name__)


class OkPostsPage(AbstractOkPageObject):

    @staticmethod
    def main_feed_locator():
        return By.CLASS_NAME, 'media_feed'

    def load_more(self):
        return self.driver.find_element(By.CLASS_NAME, 'js-show-more')

    def feed_units(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '#hook_Loader_FriendStatusesMRBLoader .feed')

    def collect_post(self) -> Generator[SmPostDto, None, None]:
        self.navigate_to(self.link_strategy.get_posts_page())
        self.get_wait().until(EC.presence_of_element_located(self.main_feed_locator()))
        html_body = self.driver.find_element(By.XPATH, '//body')

        self.init_end_of_page_count()
        while True:
            for i in range(20):
                html_body.send_keys(Keys.END)

            self._wait_until_timeline_settles()

            if self.is_end_of_page():
                for post in self._fetch_posts():
                    yield post

                try:
                    self.init_end_of_page_count()
                    btn = self.load_more()
                    self.scroll_into_view(btn)
                    btn.click()
                except (NoSuchElementException, ElementNotInteractableException):
                    return

    def _fetch_posts(self) -> Generator[SmPostDto, None, None]:
        for node in self.feed_units():
            dto = OkSinglePostPage(self.driver, self.link_strategy).fetch(node)
            self._clear_post(node)
            yield dto

    def _clear_post(self, node: WebElement):
        self.driver.execute_script(
            "arguments[0].remove()",
            node
        )

    def _wait_until_timeline_settles(self):
        self.get_wait().until(
            self.check_time_line_settled('#hook_Loader_FriendStatusesMRBLoader > div:first-child', None))
