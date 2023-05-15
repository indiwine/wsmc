import logging
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional, Generator

from django.conf import settings
from selenium.common import WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Remote
from seleniumwire import webdriver as seleniumwire_webdriver
from seleniumwire.utils import decode

logger = logging.getLogger(__name__)

WEB_DRIVER = Remote

class WsmcWebDriver(WEB_DRIVER):
    SELENIUMWIRE_OPTIONS = {
        "addr": socket.gethostname(),
        'request_storage': 'memory',
        'request_storage_max_size': 100
    }

    is_seleniumwire = False

    def __init__(self, **kwargs):
        if issubclass(WEB_DRIVER, seleniumwire_webdriver.Remote):
            self.is_seleniumwire = True
            kwargs['seleniumwire_options'] = self.SELENIUMWIRE_OPTIONS

        super().__init__(**kwargs)

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
        if not self.is_seleniumwire:
            logger.debug('Iterating over non selenium wire instance')
            return
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
        if not self.is_seleniumwire:
            logger.debug('Iterating over non seleniumwire instance')
            return

        logger.debug(f'Iterating true {len(self.requests)} requests')

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

    def is_element_displayed_safe(self, element: WebElement) -> bool:
        try:
            return element.is_displayed()
        except WebDriverException as e:
            logger.warning('is_element_displayed_safe failed to check', exc_info=e)
            return False
