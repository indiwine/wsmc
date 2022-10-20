from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractvkpageobject import AbstractVkPageObject


class VkMainFeedPage(AbstractVkPageObject):
    def main_feed_container_locator(self):
        return By.ID, 'main_feed'

    def wait_for_main_feed(self):
        self.get_wait().until(EC.presence_of_element_located(self.main_feed_container_locator()))
