import logging
import re
import socket
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Generator

from django.conf import settings
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.options import FirefoxProfile, Options as FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
# from selenium import webdriver
from seleniumwire import webdriver
from seleniumwire.utils import decode

logger = logging.getLogger(__name__)


class WsmcWebDriver(webdriver.Remote):
    def save_screenshot_safe(self, prefix: str = '') -> Optional[Path]:
        dir_path = Path(f'{settings.MEDIA_ROOT}/{settings.WSMC_SELENIUM_SCREENSHOT_DIR}')
        dir_path.mkdir(exist_ok=True)

        now = datetime.now()
        if prefix:
            prefix += '_'

        file_name = dir_path / f'{prefix}{now.strftime("%d-%m-%Y_%H-%M-%S")}.png'

        try:
            self.save_screenshot(str(file_name))
            return file_name
        except Exception as e:
            logger.error('Error occurred while creating screenshot', exc_info=e)
            return None

    def clear_requests(self) -> None:
        logger.debug('Clearing fetched requests')
        del self.requests

    @property
    def get_current_url_safe(self):
        try:
            return self.current_url
        except Exception:
            logger.error('current_url annot be determent')
            return None

    def scroll_into_view(self, element: WebElement):
        self.execute_script('arguments[0].scrollIntoView({ behavior: "instant", block: "center", inline: "center" });', element)

    def is_element_at_page_and_visible(self, css_selector: str) -> bool:
        return self.execute_script("""
        var elem = document.querySelector(arguments[0]);
        if (!elem) {
            return false;
        }        
        var rect = elem.getBoundingClientRect();

        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && 
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) 
        );
        """, css_selector)

    def remove_element(self, element: WebElement) -> None:
        """
        Remove given element from the DOM
        @param element:
        """
        self.execute_script(
            "arguments[0].remove()",
            element
        )

    def is_element_has_class(self, element: WebElement, class_name: str) -> bool:
        """
        Check whenever element has a css class
        @param element: web element to check
        @param class_name: class name (without a leading dot)
        @return: True if the given class is set for an element, False otherwise
        """
        return self.execute_script(f"return arguments[0].classList.contains('{class_name}')", element)

    def request_iterator(self) -> Generator[str, None, None]:
        logger.debug(f'Iterating true {len(self.driver.requests)} requests')
        for request in self.requests:
            response = request.response
            if response and response.status_code == 200:
                yield decode(response.body, response.headers.get('Content-Encoding', 'identity')).decode()
            else:
                logger.error('No response')
        self.clear_requests()

    def get_current_document_height(self) -> int:
        return self.execute_script("return document.body.scrollHeight")

    def quit_safe(self):
        logger.info('Closing selenium driver')
        try:
            self.quit()
        except Exception as e:
            logger.error('Error while quiting webdriver', exc_info=e)


class SeleniumDriverTypeEnum(Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


def grp(pat, txt):
    r = re.search(pat, txt)
    if r:
        ver_number = r.group(1)
        return int(ver_number.replace('.', ''))

    return '&'


class DriverBuilder:
    @staticmethod
    def build() -> WsmcWebDriver:

        selected_driver = DriverBuilder._get_selected_driver()
        logger.debug(f'Building webdriver {selected_driver.name}')
        options = DriverBuilder._get_driver_options(selected_driver)
        capabilities = options.to_capabilities()
        seleniumwire_options = {
            "addr": socket.gethostname(),
            'request_storage': 'memory',
            'request_storage_max_size': 100
        }
        logger.debug(f'Webdriver executor: {settings.WSMC_WEBDRIVER_URL}')
        driver = WsmcWebDriver(command_executor=settings.WSMC_WEBDRIVER_URL,
                                  options=options,
                                  browser_profile=DriverBuilder._get_browser_profile(selected_driver),
                                  desired_capabilities=capabilities,
                                  seleniumwire_options=seleniumwire_options
                                  )

        driver.set_page_load_timeout(settings.WSMC_SELENIUM_WAIT_TIMEOUT)

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
    def _get_driver_options(selected_driver: SeleniumDriverTypeEnum) -> ArgOptions:
        if selected_driver == SeleniumDriverTypeEnum.CHROME:
            user_agent_faker = UserAgent(browsers=['edge', 'chrome', 'safari', 'opera'])
            user_agent_faker.update()
            ua = user_agent_faker.chrome
            logger.debug(f'UA: {ua}')

            options = ChromeOptions()
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.images": 2,
                'intl.accept_languages': settings.WSMC_WEBDRIVER_LOCALE
            }
            options.add_experimental_option('prefs', prefs)
            options.add_argument(f'--lang={settings.WSMC_WEBDRIVER_LOCALE}')

            options.add_argument("--disable-blink-features")
            # options.add_argument(f'user-agent={ua}')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("start-maximized")
            options.add_extension('/app/social_media/webdriver/uBlock-Origin.crx')
            options.add_extension('/app/social_media/webdriver/Privacy-Pass.crx')
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
