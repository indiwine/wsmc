import json
import logging
import re
from dataclasses import asdict
from typing import Optional

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import SmProfileDto
from .abstractvkpageobject import AbstractVkPageObject
from .api_objects.vkprofilenode import VkProfileNode
from .vkprofilewallpage import VkProfileWallPage
from ...common import recursive_dict_search
from ...exceptions import WsmcWebDriverProfileException

logger = logging.getLogger(__name__)


class VkProfilePage(AbstractVkPageObject):
    _user_id: Optional[int] = None

    @staticmethod
    def profile_container_locator():
        return By.ID, 'profile_redesigned'

    def wall_link(self):
        return self.driver.find_element(By.XPATH, '//div[@id="profile_wall"]//li[@class="_wall_tab_own"]/a[@href]')

    def submit_post_box(self):
        return self.driver.find_element(By.ID, 'submit_post_box')

    def go_to_wall(self):
        self._navigate_if_necessary()
        self.navigate_to(self.wall_link().get_attribute('href'))
        return VkProfileWallPage(self.driver, self.link_strategy)

    def collect_profile(self) -> SmProfileDto:
        logger.debug('Collecting profile information')
        self.clear_requests()
        self._navigate_if_necessary()
        self._user_id = self._extract_user_id()
        profile = self._find_profile_data()
        return self._node_to_dto(profile, self._user_id)

    def _navigate_if_necessary(self):
        profile_link = self.link_strategy.get_profile_link()
        if self.driver.current_url != profile_link:
            self.navigate_to(profile_link)
            self.get_wait().until(EC.presence_of_element_located(self.profile_container_locator()))

    def _find_profile_data(self) -> VkProfileNode:
        for body in self.request_iterator():
            profile_found = self._process_request(body)
            if profile_found:
                return profile_found
        raise WsmcWebDriverProfileException('Cannot find profile inforamtions')

    def _process_request(self, raw_json: str) -> Optional[VkProfileNode]:
        raw_data = json.loads(raw_json)
        for node in recursive_dict_search(raw_data, 'users.get'):
            user_data = self._process_user_node(node)
            if user_data:
                return VkProfileNode(user_data)

        return None

    def _process_user_node(self, node) -> Optional[dict]:
        if isinstance(node, list):
            for item in node:
                if isinstance(item, dict) and 'id' in item and item['id'] == self._user_id:
                    logger.info('User information found')
                    return item
        return None

    def _extract_user_id(self) -> int:
        oid = self._try_get_user_id_from_submit_box()
        if oid is None:
            pass
        oid = self._try_get_user_id_from_wall_link()

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
        wall_link = self.wall_link().get_attribute('href')
        match = pattern.search(wall_link)

        if match is None:
            raise WsmcWebDriverProfileException(f'Cannot locate "/wall" in wall url: "{wall_link}"')

        oid = match.group('oid')
        return int(oid)

    @staticmethod
    def _node_to_dto(node: VkProfileNode, oid) -> SmProfileDto:
        dto = SmProfileDto(name=node.name,
                           location=node.location,
                           home_town=node.home_town,
                           university=node.education,
                           birthdate=node.birthday,
                           oid=oid
                           )
        logger.info(f'Profile info found: {json.dumps(asdict(dto), indent=2, ensure_ascii=False, default=str)}')
        return dto
