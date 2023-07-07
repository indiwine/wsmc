import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .abstractvkpageobject import AbstractVkPageObject
from .vkauthpage import VkAuthPage
from .vkmainfeedpage import VkMainFeedPage
from ...exceptions import WsmcWebDriverLoginError

logger = logging.getLogger(__name__)


class VkLoginPage(AbstractVkPageObject):

    def captcha_window_locator(self):
        return By.CLASS_NAME, 'vkc__Captcha__container'

    def email_input_locator(self):
        return By.ID, 'index_email'

    def email_input(self):
        return self.driver.find_element(*self.email_input_locator())

    def submit_button(self):
        return self.driver.find_element(By.XPATH, '//div[@id="index_login"]//button[@type="submit"]')

    def perform_login(self, user_name: str, password: str):
        self.navigate_to(self.link_strategy.base_url)
        self.get_wait().until(
            EC.any_of(
                EC.visibility_of_element_located(self.email_input_locator()),
                EC.visibility_of_element_located(VkMainFeedPage.main_feed_container_locator()),
            )
        )
        if self.driver.find_element_safe(*self.email_input_locator()):
            return self._do_login(user_name, password)

        logger.info('Already logged in... skipping')

    def _do_login(self, user_name: str, password: str):
        self.email_input().send_keys(user_name)
        self.submit_button().click()
        try:
            auth_page = VkAuthPage(self.driver, self.link_strategy)
            main_feed_page = auth_page.set_password(password)
            main_feed_page.wait_for_main_feed()
        except TimeoutException:
            err_msg = f'Username or password incorrect for "{user_name}"'
            is_captcha = False
            if self.driver.find_element_safe(*self.captcha_window_locator()):
                is_captcha = True
                err_msg = f'Captcha required for "{user_name}"'

            raise WsmcWebDriverLoginError(err_msg, is_captcha_required=is_captcha)
