import json
import logging
import urllib.parse
from typing import Generator
from dataclasses import asdict

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media import SocialMediaTypes
from .abstractvkpageobject import AbstractVkPageObject
from ...common import date_time_parse

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
            yield self._process_post_node(post_node)

    def _process_post_node(self, node: WebElement) -> SmPostDto:
        post_date = date_time_parse(node.find_element(By.CLASS_NAME, 'post_date').get_attribute('textContent'))
        dto = SmPostDto(sm_post_id=node.get_attribute('data-post-id'),
                        datetime=post_date,
                        social_media=SocialMediaTypes.VK.value
                        )

        dto.permalink = node.find_element(By.CLASS_NAME, 'post_link').get_attribute('href')
        body_node = node.find_element(By.CLASS_NAME, 'wall_text')
        self._remove_more_button(body_node)
        dto.body = body_node.get_attribute('textContent').strip()
        if len(dto.body) == 0:
            dto.body = None

        d_dict = asdict(dto)
        logger.info(f'VK post found: {json.dumps(d_dict, indent=2, ensure_ascii=False, default=str)}')
        return dto

    def _remove_more_button(self, body_node: WebElement):
        self.driver.execute_script("""
        var body_node = arguments[0]
        body_node.getElementsByClassName('wall_post_more').forEach(el => el.remove())
        """, body_node)

    def get_max_offset(self) -> int:
        parse_result = urllib.parse.urlparse(self.last_page_link().get_attribute('href'))
        params = urllib.parse.parse_qs(parse_result[4])
        return int(params['offset'][0])
