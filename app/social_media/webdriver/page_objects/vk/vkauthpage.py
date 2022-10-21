from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractvkpageobject import AbstractVkPageObject
from .vkmainfeedpage import VkMainFeedPage


class VkAuthPage(AbstractVkPageObject):

    def password_locator(self):
        return By.XPATH, '//input[@name="password"]'

    def password_field(self):
        return self.driver.find_element(*self.password_locator())

    def get_submit_button(self):
        return self.driver.find_element(By.XPATH, '//button[@type="submit"]')

    def set_password(self, password: str) -> VkMainFeedPage:
        self.get_wait().until(EC.visibility_of_element_located(self.password_locator()))
        self.password_field().send_keys(password)
        self.get_submit_button().click()
        return VkMainFeedPage(self.driver, self.link_strategy)
