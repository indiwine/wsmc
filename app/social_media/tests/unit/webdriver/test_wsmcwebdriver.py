from django.conf import settings
from django.test import SimpleTestCase
from selenium.common import TimeoutException

from social_media.webdriver import DriverBuilder
from social_media.webdriver.wsmcwebdriver import WsmcWebDriver


class TestWsmcWebdriver(SimpleTestCase):
    driver: WsmcWebDriver

    def setUp(self) -> None:
        self.driver: WsmcWebDriver = DriverBuilder.build()

    def tearDown(self) -> None:
        self.driver.quit()

    def test_execute_async_timeout(self):
        additional_delay = 60
        wait_sec = settings.WSMC_SELENIUM_SCRIPT_TIMEOUT + additional_delay

        def do_long_async_task():
            self.driver.execute_async_script("""
            const callback = arguments[arguments.length - 1];
            setTimeout(callback, arguments[0] * 1000);
            """, wait_sec)

        self.assertRaises(TimeoutException, do_long_async_task)

    def test_save_and_restore_state(self):
        self.driver.get('http://vk.com')
        print(self.driver.get_cookies())

