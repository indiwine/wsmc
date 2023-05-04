import datetime
import logging
from abc import ABC
from functools import partial
from pathlib import Path
from time import sleep
from typing import Generator, Optional, Callable, TypeVar, List, Type

from django.conf import settings
from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait, POLL_FREQUENCY
from seleniumwire.utils import decode
from seleniumwire.webdriver import Remote

from social_media.webdriver.exceptions import WscmWebdriverRetryFailedException

logger = logging.getLogger(__name__)

T = TypeVar('T')


class AbstractPageObject(ABC):
    # Number of loops without change before timeline will be consigned "settled"
    _TIMELINE_LOOP_SETTLED_COUNT = 10

    NAVIGATE_MAX_RETRY_COUNT = 10

    _is_eop_inited: bool = False
    _eop_last_height: int = 0

    _previous_children_count = 0
    _loops_with_no_change = 0

    def __init__(self, driver: Remote):
        self.driver = driver

    def get_wait(self, timeout: float = settings.WSMC_SELENIUM_WAIT_TIMEOUT,
                 poll_frequency: float = POLL_FREQUENCY) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout, poll_frequency)

    def navigate_to(self, location: str) -> None:
        """
        Navigate to a given location
        @param location:
        """
        self.retry_action(lambda: self.driver.get(location))

    def retry_action(self,
                     action: Callable[[], T],
                     max_retry_count: int = 10,
                     on_fail: Optional[Callable] = None,
                     additional_exceptions: List[Type[Exception]] = None,
                     cooldown_time: Optional[int] = None
                     ) -> T:
        """
        Basic action that can be repeated up to `max_retry_count` after a refresh action

        Action is expecting to raise a selenium TimeoutException
        @param cooldown_time: optional number of seconds between attempts
        @param additional_exceptions: List exceptions eligible for retry (selenium.common.TimeoutException is always present)
        @param action: callback
        @param max_retry_count: maximum number retries
        @param on_fail: Called one time at first error
        @return:
        """

        exceptions_to_wait: List[Type[Exception]] = [TimeoutException]
        if additional_exceptions:
            exceptions_to_wait += additional_exceptions

        retry_count = 0
        while True:
            retry_count += 1
            try:
                if retry_count > 1:
                    logger.info(f'Action failed. Retry num: {retry_count}')
                return action()
            except tuple(exceptions_to_wait) as e:
                if retry_count == 1 and on_fail:
                    on_fail()

                if retry_count >= max_retry_count:
                    self.save_screenshot('max_retry_reached')
                    raise WscmWebdriverRetryFailedException('Retry max count reached')

                if cooldown_time:
                    logger.error(f'Action failed... reloading page in {cooldown_time}s', exc_info=e)
                    sleep(cooldown_time)
                else:
                    logger.error('Action failed... reloading page', exc_info=e)

                self.driver.refresh()

    def save_screenshot(self, prefix: str = '') -> Optional[Path]:
        dir_path = Path(f'{settings.MEDIA_ROOT}/{settings.WSMC_SELENIUM_SCREENSHOT_DIR}')
        dir_path.mkdir(exist_ok=True)

        now = datetime.datetime.now()
        if prefix:
            prefix += '_'

        file_name = dir_path / f'{prefix}{now.strftime("%d-%m-%Y_%H-%M-%S")}.png'

        try:
            self.driver.save_screenshot(str(file_name))
            return file_name
        except Exception as e:
            logger.error('Error occurred while creating screenshot', exc_info=e)
            return None

    def clear_requests(self) -> None:
        logger.debug('Clearing fetched requests')
        del self.driver.requests

    def scroll_into_view(self, element: WebElement):
        self.driver.execute_script('arguments[0].scrollIntoView({block: "center", inline: "center"});', element)

    def is_element_at_page_and_visible(self, css_selector: str) -> bool:
        return self.driver.execute_script("""
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
        self.driver.execute_script(
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
        return self.driver.execute_script(f"return arguments[0].classList.contains('{class_name}')", element)

    def request_iterator(self) -> Generator[str, None, None]:
        logger.debug(f'Iterating true {len(self.driver.requests)} requests')
        for request in self.driver.requests:
            response = request.response
            if response and response.status_code == 200:
                yield decode(response.body, response.headers.get('Content-Encoding', 'identity')).decode()
            else:
                logger.error('No response')
        self.clear_requests()

    def init_end_of_page_count(self):
        self._is_eop_inited = True
        self._eop_last_height = self._get_current_document_height()

    def _get_current_document_height(self) -> int:
        return self.driver.execute_script("return document.body.scrollHeight")

    def is_end_of_page(self):
        if not self._is_eop_inited:
            raise RuntimeError('End of page counter is not inited, please call init_end_of_page_count() beforehand')

        current_height = self._get_current_document_height()
        logger.debug(f'Current page height: {current_height}')

        is_nowhere_to_scroll = current_height == self._eop_last_height
        if not is_nowhere_to_scroll:
            self._eop_last_height = current_height

        if is_nowhere_to_scroll:
            logger.info('END OF PAGE reached')

        return is_nowhere_to_scroll

    def check_time_line_settled(self, child_css: str, loader_css: Optional[str]) -> Callable[[Remote], bool]:
        """
        A "wait" callback that waits until the number of child elements remains unchanged.

        Optionally checks whatever is loader visible or not (in a viewport).
        @param child_css: css sector for the element on which we can get "childElementCount"
        @param loader_css: css selector for a "loader" container
        @return: Callable for `until()` method
        """
        return partial(self._is_time_line_settled, child_css, loader_css)

    def _is_time_line_settled(self, child_css: str, loader_css: Optional[str], driver) -> bool:
        logger.debug('Checking if timeline settled')
        child_count = self.driver.execute_script(
            "return document.querySelector(arguments[0]).childElementCount", child_css)
        logger.debug(f'Checking container child number: {child_count}')

        loader_is_in_view = False
        if loader_css:
            loader_is_in_view = self.is_element_at_page_and_visible(loader_css)
            logger.debug(f'Loader is in view: {loader_is_in_view}')

        if child_count == self._previous_children_count:
            self._loops_with_no_change = self._loops_with_no_change + 1
            logger.debug('Timeline: no change in child number')
        else:
            logger.debug('Timeline: child number changed')
            self._loops_with_no_change = 0

        self._previous_children_count = child_count
        loop_ends = self._loops_with_no_change == self._TIMELINE_LOOP_SETTLED_COUNT
        if loop_ends:
            logger.info('Timeline: settled')
            self._loops_with_no_change = 0
        return loop_ends and not loader_is_in_view
