from ..abstrtactpageobject import AbstractPageObject
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
class FacebookRegionPage(AbstractPageObject):

    def get_title(self):
        return self.driver.find_element(By.TAG_NAME, 'h2')

    def get_name(self, url: str) -> str:
        self.driver.get(url)
        self.get_wait().until(EC.presence_of_element_located((By.TAG_NAME, 'h2')))
        return self.get_title().text