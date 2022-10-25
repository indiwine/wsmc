from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from social_media.webdriver.exceptions import WsmcWebDriverLoginError
from .abstractokpageobject import AbstractOkPageObject


class OkLoginPage(AbstractOkPageObject):

    @staticmethod
    def field_email_locator():
        return By.ID, 'field_email'

    @staticmethod
    def main_feed_locator():
        return By.CLASS_NAME, 'main-feed'

    def field_email(self):
        return self.driver.find_element(*self.field_email_locator())

    def field_password(self):
        return self.driver.find_element(By.ID, 'field_password')

    def submit_btn(self):
        return self.driver.find_element(By.CSS_SELECTOR, '.login-form-actions input[type=submit]')

    def login_error(self):
        return self.driver.find_element(By.CLASS_NAME, 'login_error')

    def perform_login(self, user_name: str, password: str):
        self.navigate_to(self.link_strategy.basic_url)
        self.get_wait().until(EC.presence_of_element_located(self.field_email_locator()))
        self.field_email().send_keys(user_name)
        self.field_password().send_keys(password)
        self.submit_btn().click()

        try:
            self.get_wait().until(EC.presence_of_element_located(self.main_feed_locator()))
        except TimeoutException:
            raise WsmcWebDriverLoginError(self._get_login_error_str())

    def _get_login_error_str(self) -> str:
        try:
            err_element = self.login_error()
            result = err_element.get_property('textContent')
        except NoSuchElementException:
            result = 'Unknown error'

        return result
