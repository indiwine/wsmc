from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractokpageobject import AbstractOkPageObject


class OkAboutProfilePage(AbstractOkPageObject):

    @staticmethod
    def profile_summary_locator():
        return By.CLASS_NAME, 'user-profile __summary'

    def collect_data(self):
        self.navigate_to(self.link_strategy.get_profile_about())
        self.get_wait().until(EC.presence_of_element_located(self.profile_summary_locator()))
