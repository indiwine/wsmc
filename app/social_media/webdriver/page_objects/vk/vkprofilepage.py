import json
import logging
import re
from dataclasses import asdict
from typing import Optional
from urllib.parse import urlparse

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import SmProfileDto, SmProfileMetadata
from .abstractvkpageobject import AbstractVkPageObject
from .api_objects.vkprofilenode import VkProfileNode
from .vkprofilewallpage import VkProfileWallPage
from ...common import recursive_dict_search
from ...exceptions import WsmcWebDriverProfileException, WsmcWebDriverProfileNotFoundException

logger = logging.getLogger(__name__)


class VkProfilePage(AbstractVkPageObject):
    NOT_FOUND_TITLE = '404 Not Found'
    VK_USER_GET = 'users.get'
    _user_id: Optional[int] = None
    _user_domain: Optional[str] = None

    @staticmethod
    def profile_container_locator():
        return By.ID, 'profile_redesigned'

    @staticmethod
    def tab_placeholder():
        return By.CLASS_NAME, 'TabItemSkeleton__placeholder'

    def wall_link(self):
        return self.driver.find_element(By.XPATH, '//div[@id="profile_wall"]//li[@class="_wall_tab_own"]/a[@href]')

    def empty_wall_link(self):
        return self.driver.find_element(By.XPATH, '//li[@class="page_wall_no_posts"]/a[@href]')

    def submit_post_box(self):
        return self.driver.find_element(By.ID, 'submit_post_box')

    def prefetch_script_node(self):
        return self.driver.find_element(By.XPATH, '//script[contains(text(),"apiPrefetchCache")]')

    def find_wall_link(self) -> Optional[str]:
        try:
            return self.wall_link().get_attribute('href')
        except NoSuchElementException:
            logger.debug('Regular wall link was not found... trying empty wall link')

        try:
            return self.empty_wall_link().get_attribute('href')
        except NoSuchElementException:
            logger.debug('Empty wall link failed')

        return None

    def go_to_wall(self):
        self.navigate_if_necessary()
        self.navigate_to(self.find_wall_link())
        return VkProfileWallPage(self.driver, self.link_strategy)

    def collect_profile(self) -> SmProfileDto:
        """
        @raise WsmcWebDriverProfileNotFoundException
        @return:
        """
        logger.debug('Collecting profile information')
        self.driver.clear_requests()
        self.navigate_if_necessary()
        self.get_wait().until(EC.any_of(
            EC.invisibility_of_element_located(self.tab_placeholder()),
            EC.title_is(self.NOT_FOUND_TITLE)
        ))


        self._extract_url_components()

        # self._user_id = self._extract_user_id()

        profile = self._find_profile_data()
        return self._node_to_dto(profile)

    def navigate_if_necessary(self):
        """
        @raise WsmcWebDriverProfileNotFoundException
        """
        profile_link = self.link_strategy.get_profile_link()
        if self.driver.current_url != profile_link:
            self.navigate_to(profile_link)

            self.get_wait().until(EC.any_of(
                EC.presence_of_element_located(self.profile_container_locator()),
                EC.title_is(self.NOT_FOUND_TITLE)
            ))

            if self.driver.title == self.NOT_FOUND_TITLE:
                raise WsmcWebDriverProfileNotFoundException(f'Profile "{self.driver.get_current_url_safe}" not found')

    def _find_profile_data(self) -> VkProfileNode:
        profile_found = self._try_extract_prefetch_cache()

        if not profile_found:
            logger.debug(f'Direct prefetch method failed... Reloading cache')
            is_success = self._reload_prefetch_cache()
            if is_success:
                profile_found = self._try_extract_prefetch_cache()

        if profile_found:
            return profile_found

        for body in self.driver.request_iterator():
            profile_found = self._process_request(body)
            if profile_found:
                return profile_found

        raise WsmcWebDriverProfileException('Cannot find profile information: All methods failed')

    def _try_extract_prefetch_cache(self) -> Optional[VkProfileNode]:
        logger.debug('Trying to find profile data using prefetch cache method')
        prefetch_data = self.driver.execute_script('return window.cur.apiPrefetchCache')
        if prefetch_data and isinstance(prefetch_data, list):
            for item in prefetch_data:
                if item['method'] == self.VK_USER_GET:
                    user_data = self._process_user_node(item['response'])
                    if user_data:
                        logger.debug('Prefetch cache method succeed')
                        return VkProfileNode(user_data)
        logger.debug('Prefetch cache method failed')
        return None

    def _reload_prefetch_cache(self):
        try:
            script_node = self.prefetch_script_node()
            self.driver.execute_script('eval(arguments[0].textContent)', script_node)
            return True
        except NoSuchElementException:
            logger.debug('Prefetch script node does not exist. Nothing to reload.')
            return False

    def _process_request(self, raw_json: str) -> Optional[VkProfileNode]:
        logger.debug('Trying to find profile data using XHR method')
        raw_data = json.loads(raw_json)
        for node in recursive_dict_search(raw_data, self.VK_USER_GET):
            user_data = self._process_user_node(node)
            if user_data:
                logger.debug('XHR method succeed')
                return VkProfileNode(user_data)

        return None

    def _process_user_node(self, node) -> Optional[dict]:
        if isinstance(node, list):
            for item in node:
                if isinstance(item, dict):
                    same_id = self._user_id and 'id' in item and item['id'] == self._user_id
                    same_domain = self._user_domain and 'domain' in item and item['domain'] == self._user_domain
                    if same_id or same_domain:
                        logger.info('User information found')
                        return item
        return None

    def _extract_user_id(self) -> int:
        oid = self._try_get_user_id_from_submit_box()
        if oid is None:
            oid = self._try_get_user_id_from_wall_link()

        if oid is None:
            raise WsmcWebDriverProfileException('Cannot find user id')

        logger.debug(f'Found user id: {oid}')
        return oid

    def _try_get_user_id_from_submit_box(self) -> Optional[int]:
        logger.debug('Trying to find VK user id using submit box method')
        try:
            wrapper = self.submit_post_box()
            oid = wrapper.get_attribute('data-oid')
            return int(oid)
        except NoSuchElementException:
            logger.debug('Submit box method failed')
            return None

    def _try_get_user_id_from_wall_link(self) -> int:
        logger.debug('Trying to find VK user id using wall link method')

        pattern = re.compile(r"\/wall(?P<oid>\d+)")
        wall_link = self.find_wall_link()
        if not wall_link:
            return None

        match = pattern.search(wall_link)

        if match is None:
            raise WsmcWebDriverProfileException(f'Cannot locate "/wall" in wall url: "{wall_link}"')

        oid = match.group('oid')
        return int(oid)

    def _extract_url_components(self):
        path_component = self.link_strategy.get_last_path_component()
        logger.debug(f'Analyzing URL path component: "{path_component}"')

        id_pattern = re.compile(r"id(?P<oid>\d+)")
        match = id_pattern.search(path_component)
        if match:
            self._user_id = int(match.group('oid'))
            logger.debug(f'User id found from an url: {self._user_id}')
            return

        logger.debug('Looks like url in a "domain" notation, using it for search for user data')
        self._user_domain = path_component

    @staticmethod
    def _node_to_dto(node: VkProfileNode) -> SmProfileDto:
        dto = node.to_dto()
        logger.info(f'Profile info found: {json.dumps(asdict(dto), indent=2, ensure_ascii=False, default=str)}')
        return dto
