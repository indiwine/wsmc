from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractvkpageobject import AbstractVkPageObject
from .vkauthpage import VkAuthPage


class VkLoginPage(AbstractVkPageObject):

    def email_input_locator(self):
        return By.ID, 'index_email'

    def email_input(self):
        return self.driver.find_element(*self.email_input_locator())

    def submit_button(self):
        return self.driver.find_element(By.XPATH, '//div[@id="index_login"]//button[@type="submit"]')

    def perform_login(self, user_name: str, password: str):
        self.navigate_to('https://vk.com/')
        self.get_wait().until(EC.visibility_of_element_located(self.email_input_locator()))
        self.email_input().send_keys(user_name)
        self.submit_button().click()
        auth_page = VkAuthPage(self.driver, self.link_strategy)
        main_feed_page = auth_page.set_password(password)
        main_feed_page.wait_for_main_feed()

