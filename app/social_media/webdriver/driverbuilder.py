import logging
import socket
from enum import Enum

from django.conf import settings
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.options import FirefoxProfile, Options as FirefoxOptions
# from selenium import webdriver
from seleniumwire import webdriver

logger = logging.getLogger(__name__)


class SeleniumDriverTypeEnum(Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


class DriverBuilder:
    @staticmethod
    def build():

        selected_driver = DriverBuilder._get_selected_driver()
        logger.debug(f'Building webdriver {selected_driver.name}')
        options = DriverBuilder._get_driver_options(selected_driver)
        capabilities = options.to_capabilities()
        seleniumwire_options = {
            "addr": socket.gethostname()
        }
        logger.debug(f'Webdriver executor: {settings.WSMC_WEBDRIVER_URL}')
        driver = webdriver.Remote(command_executor=settings.WSMC_WEBDRIVER_URL,
                                  options=options,
                                  browser_profile=DriverBuilder._get_browser_profile(selected_driver),
                                  desired_capabilities=capabilities,
                                  seleniumwire_options=seleniumwire_options
                                  )
        driver.scopes = [
            '.*facebook\.com/api/graphql.*',
            '.*api\.vk\.com/method/execute.*'
        ]
        return driver

    @staticmethod
    def _get_selected_driver() -> SeleniumDriverTypeEnum:
        raw_driver = settings.WSMC_SELENIUM_DRIVER
        for item in SeleniumDriverTypeEnum:
            if item.value == raw_driver:
                return item

        raise RuntimeError(f'{raw_driver} is not a valid selenium web driver')

    @staticmethod
    def _get_driver_options(selected_driver: SeleniumDriverTypeEnum) -> ArgOptions:
        if selected_driver == SeleniumDriverTypeEnum.CHROME:
            options = ChromeOptions()
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                # "profile.managed_default_content_settings.images": 2
            }
            options.add_experimental_option('prefs', prefs)
            options.add_argument(f'--lang={settings.WSMC_WEBDRIVER_LOCALE}')

            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("start-maximized")
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
