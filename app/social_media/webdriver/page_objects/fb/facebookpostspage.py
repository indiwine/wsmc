import json
import logging
from datetime import date
from typing import Generator

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media.socialmediatypes import SocialMediaTypes
from .abstractfbpageobject import AbstractFbPageObject
from .api_objects.FacebookPostNode import FacebookPostNode
from .facebookpostsfilterdialogfragment import FacebookPostsFilterDialogFragment
from ...common import recursive_dict_search

logger = logging.getLogger(__name__)

# Number of page "scrolls" before loop will be considered finished
_MAX_PAGE_SCROLLS = None


class FacebookPostsPage(AbstractFbPageObject):
    skip_count = 0
    found_count = 0

    def get_timeline_scripts(self) -> list[WebElement]:
        return self.driver.find_elements(By.XPATH, '//script[@data-sjs][contains(text(),"Story")]')

    def get_profile_timeline(self):
        return self.driver.find_element(*self.get_profile_timeline_locator())

    @staticmethod
    def get_profile_timeline_locator():
        return By.XPATH, '//div[@data-pagelet="ProfileTimeline"]'

    def navigate_to_profile(self, profile: str):
        self.navigate_to(profile)
        self.get_wait().until(EC.presence_of_element_located(self.get_profile_timeline_locator()))

    def collect_posts(self, date_to_check: date) -> Generator[SmPostDto, None, None]:
        self.found_count = self.skip_count = 0
        logger.info('Start collecting FB posts')
        self.clear_requests()

        profile_url = self.navigation_strategy.generate_profile_link()
        if self.driver.current_url != profile_url:
            self.navigate_to_profile(profile_url)

        dialog = FacebookPostsFilterDialogFragment(self.driver).set_navigation_strategy(self.navigation_strategy)
        dialog.set_post_filter_year_month(date_to_check)
        self._wait_until_settled()

        # logger.debug('Collecting SCRIPTS from page')
        # for element in self.get_timeline_scripts():
        #     for node in self._process_raw_json(element.get_attribute('textContent')):
        #         yield self._to_dto(node)

        for node in self._process_requests():
            if not node.is_same_year_and_month(date_to_check):
                return
            self.found_count += 1
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
        self.init_end_of_page_count()
        html_body = self.driver.find_element(By.XPATH, '//body')
        scrolls_done = 0

        while not end_reached:
            logger.info('sending page down')

            for i in range(15):
                html_body.send_keys(Keys.PAGE_DOWN)

            self._wait_until_settled()

            scrolls_done += 1

            for node in self._iterate_over_requests():
                yield node

            end_reached = self.is_end_of_page()

    def _wait_until_settled(self):
        self.get_wait(poll_frequency=1, timeout=60).until(
            self.check_time_line_settled('div[data-pagelet=ProfileTimeline]',
                                         'div[role=article] > div[role=progressbar]'))

    def _iterate_over_requests(self) -> Generator[FacebookPostNode, None, None]:
        for body in self.request_iterator():
            for line in body.splitlines():
                for node in self._process_raw_json(line):
                    yield node

    def _process_raw_json(self, raw_json_str: str) -> Generator[FacebookPostNode, None, None]:
        raw_data = json.loads(raw_json_str)
        for node in recursive_dict_search(
                raw_data,
                'node',
                self._filter_story_items
        ):
            post_node = self._wrap_node_unit(node)
            logger.info(f'Fb POST found: {post_node.__str__()}')
            if post_node.is_valid_story:
                yield post_node
            else:
                self.skip_count += 1
                logger.warning(f'Skipping FB post: {post_node.get_permalink}')

    def _wrap_node_unit(self, node) -> FacebookPostNode:
        return FacebookPostNode(node)

    def _filter_story_items(self, item):
        return isinstance(item, dict) \
               and '__typename' in item \
               and '__isFeedUnit' in item \
               and item['__typename'] == 'Story' \
               and item['__isFeedUnit'] == 'Story'
