import logging

logger = logging.getLogger(__name__)
import json

from typing import Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.utils import decode

from ...common import recursive_dict_search
from ..abstrtactpageobject import AbstractPageObject
from .api_objects.FacebookPostNode import FacebookPostNode
from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media.socialmediatypes import SocialMediaTypes

LOOPS_TRESHOLD = 10


class FacebookPostsPage(AbstractPageObject):
    max_scrolls = 100

    previous_children_count = 0
    loops_with_no_change = 0

    def get_timeline_scripts(self) -> list[WebElement]:
        return self.driver.find_elements(By.XPATH, '//script[@data-sjs][contains(text(),"Story")]')

    def get_profile_timeline(self):
        return self.driver.find_element(*self.get_profile_timeline_locator())

    @staticmethod
    def get_profile_timeline_locator():
        return By.XPATH, '//div[@data-pagelet="ProfileTimeline"]'

    def collect_posts(self, profile: str) -> Generator[SmPostDto, None, None]:
        logger.info('Start collecting FB posts')
        del self.driver.requests
        self.driver.get(profile)
        self.get_wait().until(EC.presence_of_element_located(self.get_profile_timeline_locator()))

        for element in self.get_timeline_scripts():
            for node in self._process_raw_json(element.get_attribute('textContent')):
                yield self._to_dto(node)

        for node in self._process_requests():
            yield self._to_dto(node)

    @staticmethod
    def _to_dto(node: FacebookPostNode) -> SmPostDto:
        return SmPostDto(
            sm_post_id=node.get_id,
            raw_post=node.raw_node,
            datetime=node.get_creation_time_dt,
            permalink=node.get_permalink,
            body=node.get_message,
            social_media=SocialMediaTypes.FB.value
        )

    def _process_requests(self) -> Generator[FacebookPostNode, None, None]:
        end_reached = False
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        html_body = self.driver.find_element(By.XPATH, '//body')
        scrolls_done = 0

        while not end_reached:
            logger.info('sending page down')

            for i in range(15):
                html_body.send_keys(Keys.PAGE_DOWN)

            self.get_wait(poll_frequency=1, timeout=60).until(self._is_time_line_settled)

            scrolls_done += 1

            for node in self._iterate_over_requests():
                yield node

            current_height = self.driver.execute_script("return document.body.scrollHeight")
            is_nowhere_to_scroll = current_height == last_height

            if is_nowhere_to_scroll:
                logger.info('Nowhere to scroll anymore')
                end_reached = True
            if not is_nowhere_to_scroll:
                last_height = current_height

    def _iterate_over_requests(self) -> Generator[FacebookPostNode, None, None]:
        logger.info(f'Iterating true {len(self.driver.requests)} requests')
        for request in self.driver.requests:
            response = request.response
            if response and response.status_code == 200:
                body = decode(response.body, response.headers.get('Content-Encoding', 'identity')).decode()
                for line in body.splitlines():
                    for node in self._process_raw_json(line):
                        yield node
            else:
                logger.error('No response', response)
        del self.driver.requests

    def _is_time_line_settled(self, driver) -> bool:
        child_count = self.driver.execute_script(
            "return document.querySelector('div[data-pagelet=ProfileTimeline]').childElementCount")
        logger.info(f'Checking container child number: {child_count}')

        loader_is_in_view = self.driver.execute_script("""
        return (function(){
            var rect = document.querySelector('div[role=article] > div[role=progressbar]').getBoundingClientRect();
    
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
                rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
            );
        })();
        """)
        logger.info(f'Loader is in view: {loader_is_in_view}')

        if child_count == self.previous_children_count:
            self.loops_with_no_change = self.loops_with_no_change + 1
            logger.info('Loop with no change')
        else:
            self.loops_with_no_change = 0

        self.previous_children_count = child_count
        loop_ends = self.loops_with_no_change == LOOPS_TRESHOLD
        if loop_ends:
            self.loops_with_no_change = 0
        return loop_ends and not loader_is_in_view

    def _process_raw_json(self, raw_json_str: str) -> Generator[FacebookPostNode, None, None]:
        raw_data = json.loads(raw_json_str)
        for node in recursive_dict_search(
                raw_data,
                'node',
                self._filter_story_items
        ):
            post_node = self._wrap_node_unit(node)
            if post_node.is_valid_story:
                yield post_node
            else:
                logger.warning(f'Skiiping FB post: {post_node.get_permalink}')

    def _wrap_node_unit(self, node) -> FacebookPostNode:
        return FacebookPostNode(node)

    def _filter_story_items(self, item):
        return isinstance(item, dict) \
               and '__typename' in item \
               and '__isFeedUnit' in item \
               and item['__typename'] == 'Story' \
               and item['__isFeedUnit'] == 'Story'
