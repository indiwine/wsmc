import datetime
import logging

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media import SocialMediaTypes
from .abstractokpageobject import AbstractOkPageObject
from ...common import date_time_parse
from ...exceptions import WsmcWebDriverPostException, WsmcWebdriverException

logger = logging.getLogger(__name__)

SHARE_BTN_RTRY = 10
SHARE_BTN_TIMEOUT = 20


class OkSinglePostPage(AbstractOkPageObject):

    @staticmethod
    def clipboard_url():
        return By.CSS_SELECTOR, 'a[data-clipboard-url]'

    @staticmethod
    def clipboard_url_abs(element: WebElement):
        id = element.get_attribute('id')
        return By.CSS_SELECTOR, f'#{id} a[data-clipboard-url]'

    def fetch(self, element: WebElement) -> SmPostDto:
        """
        @param element:
        @return: Ready DTp
        @raise WsmcWebDriverPostException: If post cannot be properly obtained
        """
        post_id = self.share_btn(element)

        dto = SmPostDto(datetime=self._fetch_date(element),
                        sm_post_id=post_id,
                        social_media=SocialMediaTypes.OK.value,
                        permalink=self._fetch_permalink(element),
                        body=self._fetch_body(element)
                        )

        return dto

    def _fetch_date(self, element: WebElement) -> datetime.datetime:
        post_date = element.find_element(By.CLASS_NAME, 'feed_date').get_property('textContent')
        return date_time_parse(post_date)

    def _fetch_permalink(self, element: WebElement) -> str:
        return element.find_element(*self.clipboard_url()).get_attribute('data-clipboard-url')

    def _fetch_body(self, element: WebElement) -> str:
        return element.find_element(By.CLASS_NAME, 'feed_b').get_property('textContent')

    def share_btn(self, element: WebElement):
        btn = element.find_element(By.CSS_SELECTOR, 'button[data-type="RESHARE"]')
        disabled = self.driver.execute_script("return arguments[0].parentElement.classList.contains('__disabled')", btn)
        if disabled:
            logger.info(f'Share button is disabled in post "{element.text}"')
            raise WsmcWebDriverPostException(f'Post cannot be obtained, because share button is disabled.')

        def try_clik() -> btn:
            self.driver.scroll_into_view(btn)
            btn.click()
            try:
                self.get_wait(timeout=SHARE_BTN_TIMEOUT).until(
                    EC.presence_of_element_located(self.clipboard_url_abs(element)))
                return True
            except TimeoutException:
                logger.warning(f'Cannot click onto share button! Timeout after {SHARE_BTN_TIMEOUT} sec')
                return False

        click_successful = False

        for i in range(1, SHARE_BTN_RTRY):
            if try_clik():
                click_successful = True
                logger.debug(f'Share button click successful after "{i}" attempts!')
                break

        if not click_successful:
            raise WsmcWebdriverException(
                f'Click at share button failed after {SHARE_BTN_RTRY} times at post: {element.text}')

        return btn.get_attribute('data-id1')
