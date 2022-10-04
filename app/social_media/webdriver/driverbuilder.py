from enum import Enum

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import FirefoxProfile, Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


class SeleniumDriverTypeEnum(Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


class DriverBuilder:
    @staticmethod
    def build() -> WebDriver:
        selected_driver = DriverBuilder._get_selected_driver()
        return webdriver.Remote(command_executor=settings.WSMC_WEBDRIVER_URL,
                                options=DriverBuilder._get_driver_options(selected_driver),
                                browser_profile=DriverBuilder._get_browser_profile(selected_driver)
                                )

    @staticmethod
    def _get_selected_driver() -> SeleniumDriverTypeEnum:
        raw_driver = settings.WSMC_SELENIUM_DRIVER
        for item in SeleniumDriverTypeEnum:
            if item.value == raw_driver:
                return item

        raise RuntimeError(f'{raw_driver} is not a valid selenium web driver')

    @staticmethod
    def _get_driver_options(selected_driver: SeleniumDriverTypeEnum):
        if selected_driver == SeleniumDriverTypeEnum.CHROME:
            options = ChromeOptions()
            prefs = {"profile.default_content_setting_values.notifications": 2}
            options.add_experimental_option('prefs', prefs)
            options.add_argument('--lang=ru_RU')
        else:
            options = FirefoxOptions()

        return options

    @staticmethod
    def _get_browser_profile(selected_driver: SeleniumDriverTypeEnum):
        if selected_driver == selected_driver.FIREFOX:
            profile = FirefoxProfile()
            profile.set_preference("dom.webnotifications.enabled", False)
            return profile
        else:
            return None
