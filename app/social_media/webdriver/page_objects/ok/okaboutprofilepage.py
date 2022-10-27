import datetime
import re
from typing import Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import SmProfileDto
from social_media.webdriver.common import date_time_parse
from .abstractokpageobject import AbstractOkPageObject


class OkAboutProfilePage(AbstractOkPageObject):

    @staticmethod
    def profile_summary_locator():
        return By.CLASS_NAME, 'user-profile'

    def compact_profile(self):
        return self.driver.find_element(By.CLASS_NAME, 'compact-profile')

    def age(self):
        return self.driver.find_element(By.CSS_SELECTOR, '.user-profile div[data-type="AGE"]')

    def location(self):
        return self.driver.find_element(By.XPATH,
                                        "//*[contains(concat(' ',normalize-space(@class),' '),' svg-ico_home_16 ')]/../../..//DIV[@class='user-profile_i_value']")

    def birth_location(self):
        return self.driver.find_element(By.XPATH,
                                        "//*[contains(concat(' ',normalize-space(@class),' '),' svg-ico_location_16  ')]/../../..//DIV[@class='user-profile_i_value']")

    def collect_data(self) -> SmProfileDto:
        self.navigate_to(self.link_strategy.get_profile_about())
        self.get_wait().until(EC.presence_of_element_located(self.profile_summary_locator()))

        dto = SmProfileDto(self.compact_profile().get_property('textContent'))
        dto.birthdate = self._get_age()
        dto.location = self._get_location()
        return dto

    def _get_age(self) -> Optional[datetime.datetime]:
        try:
            birthday = self.age().get_property('textContent')
            birthday = re.sub(r"\([\w\s]+\)", '', birthday).strip()
            return date_time_parse(birthday)
        except NoSuchElementException:
            return None

    def _get_location(self) -> Optional[str]:
        try:
            return self.location().get_property('textContent')
        except NoSuchElementException:
            pass

        try:
            return self.birth_location().get_property('textContent')
        except NoSuchElementException:
            pass

        return None
