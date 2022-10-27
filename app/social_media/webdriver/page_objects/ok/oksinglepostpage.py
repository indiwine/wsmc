import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media import SocialMediaTypes
from .abstractokpageobject import AbstractOkPageObject
from ...common import date_time_parse


class OkSinglePostPage(AbstractOkPageObject):

    @staticmethod
    def clipboard_url():
        return By.CSS_SELECTOR, 'a[data-clipboard-url]'

    @staticmethod
    def clipboard_url_abs(element: WebElement):
        id = element.get_attribute('id')
        return By.CSS_SELECTOR, f'#{id} a[data-clipboard-url]'

    def fetch(self, element: WebElement) -> SmPostDto:
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
        self.scroll_into_view(btn)
        btn.click()
        self.get_wait().until(EC.presence_of_element_located(self.clipboard_url_abs(element)))
        return btn.get_attribute('data-id1')
