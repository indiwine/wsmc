import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractfbpageobject import AbstractFbPageObject
from ...common import recursive_dict_search


class FacebookRegionPage(AbstractFbPageObject):

    def get_title(self):
        return self.driver.find_element(By.TAG_NAME, 'h2')

    def get_city_data(self):
        return self.driver.find_element(By.XPATH, '//script[@data-sjs][contains(text(),"city_data")]')

    def get_name(self, url: str) -> str:
        self.driver.get(url)
        self.get_wait().until(EC.presence_of_element_located((By.TAG_NAME, 'h2')))
        return self._extract_name()

    def _extract_name(self):
        el = self.get_city_data()
        raw_dict = json.loads(el.get_attribute('textContent'))
        for item in recursive_dict_search(raw_dict, 'city_data'):
            return item['name']
        return ''
