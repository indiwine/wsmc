import logging
import re
from enum import Enum
from typing import Optional

from django.conf import settings
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.options import FirefoxProfile, Options as FirefoxOptions

# from selenium import webdriver
from social_media.webdriver.wsmcwebdriver import WsmcWebDriver

logger = logging.getLogger(__name__)


class SeleniumDriverTypeEnum(Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


def grp(pat, txt):
    r = re.search(pat, txt)
    if r:
        ver_number = r.group(1)
        return int(ver_number.replace('.', ''))

    return '&'


class DriverBuildOptions:
    block_images: bool = True
    profile_folder_name: Optional[str] = None


class DriverBuilder:
    @staticmethod
    def build(driver_build_options: Optional[DriverBuildOptions] = None) -> WsmcWebDriver:
        if not driver_build_options:
            driver_build_options = DriverBuildOptions()

        selected_driver = DriverBuilder._get_selected_driver()
        logger.debug(f'Building webdriver {selected_driver.name}')
        options = DriverBuilder._get_driver_options(selected_driver, driver_build_options)

        logger.debug(f'Webdriver executor: {settings.WSMC_WEBDRIVER_URL}')
        driver = WsmcWebDriver(command_executor=settings.WSMC_WEBDRIVER_URL,
                               options=options
                               )

        driver.scopes = [
            # '.*\.(jpg|jpeg|png|gif|bmp).*',
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
    def _get_driver_options(selected_driver: SeleniumDriverTypeEnum,
                            driver_build_options: DriverBuildOptions) -> ArgOptions:
        if selected_driver == SeleniumDriverTypeEnum.CHROME:

            options = ChromeOptions()
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.images": 2 if driver_build_options.block_images else 0,
                "profile.managed_default_content_settings.stylesheets": 2,
                # "profile.managed_default_content_settings.cookies": 2,
                # "profile.managed_default_content_settings.javascript": 1,
                # "profile.managed_default_content_settings.plugins": 1,
                "profile.managed_default_content_settings.popups": 2,
                "profile.managed_default_content_settings.geolocation": 2,
                "profile.managed_default_content_settings.media_stream": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "intl.accept_languages": settings.WSMC_WEBDRIVER_LOCALE
            }
            options.add_experimental_option('prefs', prefs)

            if driver_build_options.profile_folder_name:
                # options.add_argument(f'--profile-directory={driver_build_options.profile_folder_name}')
                options.add_argument(
                    f'--user-data-dir=/home/seluser/{driver_build_options.profile_folder_name}')

            options.add_argument(f'--lang={settings.WSMC_WEBDRIVER_LOCALE}')

            options.add_argument("--disable-blink-features")
            # options.add_argument(f'user-agent={ua}')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("start-maximized")
            options.add_extension("/app/social_media/webdriver/uBlock-Origin.crx")
            options.add_extension("/app/social_media/webdriver/Privacy-Pass.crx")
            options.timeouts = {
                "implicit": 0,
                "pageLoad": settings.WSMC_SELENIUM_WAIT_TIMEOUT * 1000,
                "script": settings.WSMC_SELENIUM_SCRIPT_TIMEOUT * 1000
            }
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
