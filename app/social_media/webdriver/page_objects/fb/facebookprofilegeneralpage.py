import logging
import dateparser
logger = logging.getLogger(__name__)

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import SmProfileDto
from ..abstrtactpageobject import AbstractPageObject
from ...common import recursive_dict_search
from .facebookregionpage import FacebookRegionPage


class FacebookProfileGeneralPage(AbstractPageObject):

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self._proc = {
            "education": self._extract_education,
            "current_city": self._extract_current_city,
            "birthday": self._extract_birthday
        }

    @staticmethod
    def get_profile_app_section():
        return By.CSS_SELECTOR, 'div[data-pagelet=ProfileAppSection_0]'

    def get_profile_script(self):
        return self.driver.find_element(By.XPATH, '//script[@data-sjs][contains(text(),"profile_fields")]')

    def get_name_element(self):
        return self.driver.find_element(By.TAG_NAME, 'h1')

    @staticmethod
    def get_overview_url(profile: str):
        return f'{profile}/about_overview'

    @staticmethod
    def get_basic_info_url(profile: str):
        return f'{profile}/about_contact_and_basic_info'

    def collect_profile(self, profile: str) -> SmProfileDto:
        self._navigate_and_wait(self.get_overview_url(profile))
        profile_dto = SmProfileDto(name=self.get_name_element().text)
        self._extract_json_data(profile_dto)
        self._navigate_and_wait(self.get_basic_info_url(profile))
        self._extract_json_data(profile_dto)
        self._normalize_profile(profile_dto)

        return profile_dto

    def _normalize_profile(self, profile: SmProfileDto):
        if profile.birthdate is not None:
            profile.birthdate = dateparser.parse(profile.birthdate)

    def _navigate_and_wait(self, url):
        logger.debug(f'navigation to {url}')
        self.driver.get(url)
        self.get_wait().until(EC.presence_of_element_located(self.get_profile_app_section()))

    def _extract_json_data(self, profile_dto: SmProfileDto):
        raw_data = json.loads(self.get_profile_script().get_attribute('textContent'))
        self._extract_data_from_nodes(raw_data, profile_dto)

    def _extract_data_from_nodes(self, raw_data: dict, profile_dto: SmProfileDto):
        logger.debug('Trying to extract profile data from FB JSON found')
        for profile_fields in recursive_dict_search(raw_data, 'profile_fields'):
            if 'nodes' in profile_fields:
                for node in profile_fields['nodes']:
                    field_type = node['field_type']
                    if field_type in self._proc:
                        logger.debug(f'"{field_type}" field type found processing')
                        self._proc[field_type](node, profile_dto)

    def _extract_education(self, node: dict, profile_dto: SmProfileDto):
        place = node['renderer']['field']['title']['text']
        logger.debug(f'Education place found: "{place}"')
        profile_dto.university = place

    def _extract_current_city(self, node: dict, profile_dto: SmProfileDto):
        city = node['title']['text']
        if 'ranges' in node['title']:
            range = node['title']['ranges'][0]
            if range['entity']['category_type'] == 'REGION':
                city = FacebookRegionPage(self.driver).get_name(range['entity']['profile_url'])
        logger.debug(f'City found {city}')
        profile_dto.location = city

    def _extract_birthday(self, node: dict, profile_dto: SmProfileDto):
        if profile_dto.birthdate is None:
            profile_dto.birthdate = node['title']['text']
        else:
            profile_dto.birthdate += f" {node['title']['text']}"
