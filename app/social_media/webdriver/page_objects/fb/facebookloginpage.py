import logging
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractfbpageobject import AbstractFbPageObject
from ...exceptions import WsmcWebDriverLoginError

logger = logging.getLogger(__name__)


# page_url = https://www.facebook.com/
class FacebookLoginPage(AbstractFbPageObject):

    def royal_email(self):
        return self.driver.find_element(By.XPATH, "//*[@id='email']")

    def royal_pass(self):
        return self.driver.find_element(By.XPATH, "//*[@id='pass']")

    def royal_login_button(self):
        return self.driver.find_element(*self.royal_login_button_locator())

    def login_form(self):
        return self.driver.find_element(By.XPATH, '//*[@id="loginform"]')

    def cookie_policy_dialog(self):
        return self.driver.find_element(*self.cookie_policy_dialog_essential_button_locator())

    @staticmethod
    def cookie_policy_dialog_locator():
        return By.XPATH, '//div[@data-testid="cookie-policy-manage-dialog"]'

    @staticmethod
    def cookie_policy_dialog_essential_button_locator():
        return By.XPATH, '//button[@data-testid="cookie-policy-manage-dialog-accept-button"]'

    @staticmethod
    def navigation_locator():
        return By.CSS_SELECTOR, 'div[role=navigation]'

    @staticmethod
    def royal_login_button_locator():
        return By.XPATH, "//*[@data-testid = 'royal_login_button']"

    def perform_login(self, user_name: str, password: str):
        self.navigate_to(self.navigation_strategy.base_url)
        self.get_wait().until(EC.presence_of_element_located(self.royal_login_button_locator()))
        self._check_for_cookie_policy()
        self.royal_email().send_keys(user_name)
        self.royal_pass().send_keys(password)
        self.royal_login_button().click()

        try:
            self.get_wait().until(EC.presence_of_element_located(self.navigation_locator()))
        except TimeoutException:
            url = urlparse(self.driver.current_url)
            loginform = self.login_form()

            if url.path.find('/login') == -1 or loginform is None:
                raise WsmcWebDriverLoginError('Unknown error')

            err_line = loginform.text.split("\n", 1)[0]
            raise WsmcWebDriverLoginError(f'Invalid username or password: {err_line}')

    def navigations(self):
        self.driver.find_elements()

    def _check_for_cookie_policy(self):
        policy_manager = self.cookie_policy_dialog()
        if policy_manager:
            button = policy_manager.find_element(*self.cookie_policy_dialog_essential_button_locator())
            button.click()
            self.get_wait().until_not(EC.presence_of_element_located(self.cookie_policy_dialog_locator()))
