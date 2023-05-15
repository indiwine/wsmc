from typing import Generator

import logging
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import AuthorDto
from .abstractvkpageobject import AbstractVkPageObject
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy

logger = logging.getLogger(__name__)


class VkPostFansBoxPageObject(AbstractVkPageObject):
    LIKE_LOAD_TIMEOUT = 30

    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, fans_box: WebElement):
        super().__init__(driver, link_strategy)
        self.fans_box = fans_box

    @staticmethod
    def fan_rows_locator():
        return By.CSS_SELECTOR, '#wk_likes_rows .fans_fan_row'

    def get_fan_rows(self):
        return self.fans_box.find_elements(*self.fan_rows_locator())

    def all_likes_tab(self):
        return self.fans_box.find_element(By.CSS_SELECTOR, '#likes_tab_likes > .ui_tab')

    def is_all_tabs_selected(self):
        return self.driver.is_element_has_class(self.all_likes_tab(), 'ui_tab_sel')

    def box_close_button(self):
        return self.fans_box.find_element(By.CLASS_NAME, 'box_x_button')

    def load_more_btn(self):
        return self.fans_box.find_element(By.ID, 'wk_likes_more_link')

    def switch_to_all_likes_tab(self):
        self.all_likes_tab().click()
        self.get_wait().until(EC.all_of(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '.wk_wiki_content.box_loading'))),
            EC.visibility_of_element_located(self.fan_rows_locator())
        )

    def close(self):
        self.box_close_button().click()
        self.get_wait().until(EC.invisibility_of_element(self.fans_box))

    def collect_likes(self) -> Generator[AuthorDto, None, None]:
        if not self.is_all_tabs_selected():
            self.switch_to_all_likes_tab()

        while True:
            fan_rows = self.get_fan_rows()
            for fan_row in fan_rows:
                yield self.fan_row_to_author_dro(fan_row)

            self.driver.remove_element(fan_rows)

            if not self._load_more_likes():
                self.close()
                break

    def _load_more_likes(self):
        btn = self.load_more_btn()
        if not btn.is_displayed():
            return False
        btn.click()
        try:
            self.get_wait().until(EC.presence_of_element_located(self.fan_rows_locator()))
        except TimeoutException as e:
            logger.debug('Timeout while loading likes', exc_info=e)
            return False
        return True

    @classmethod
    def fan_row_to_author_dro(cls, fan_row: WebElement) -> AuthorDto:
        fan_link = fan_row.find_element(By.CLASS_NAME, 'fans_fan_lnk')
        oid, is_group = cls.parse_oid(fan_row.get_attribute('data-id'))
        return AuthorDto(
            oid=oid,
            name=fan_link.get_property('innerText'),
            url=fan_link.get_attribute('href'),
            is_group=is_group
        )
