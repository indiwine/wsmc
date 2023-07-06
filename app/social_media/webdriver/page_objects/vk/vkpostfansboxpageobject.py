import logging
from typing import Generator, List, Dict

from selenium.common import TimeoutException, WebDriverException
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

    def generate_likes(self) -> Generator[List[AuthorDto], None, None]:
        if not self.is_all_tabs_selected():
            self.switch_to_all_likes_tab()

        while True:
            yield self._browser_based_extraction()

            if not self._load_more_likes():
                self.close()
                break

    def _load_more_likes(self):
        try:
            btn = self.load_more_btn()
            if not btn.is_displayed():
                return False
            btn.click()
        except WebDriverException as e:
            logger.error('Cannot load more likes', exc_info=e)
            return False

        try:
            self.get_wait().until(EC.presence_of_element_located(self.fan_rows_locator()))
        except TimeoutException as e:
            logger.debug('Timeout while loading likes')
            return False
        return True

    def _pure_selenium_extraction(self) -> List[AuthorDto]:
        fan_rows = self.get_fan_rows()
        results = []
        for fan_row in fan_rows:
            results.append(self.fan_row_to_author_dro(fan_row))

        self.driver.remove_element(fan_rows)
        return results

    def _browser_based_extraction(self) -> List[AuthorDto]:
        fan_rows = self.get_fan_rows()

        like_objects: List[Dict] = self.driver.execute_script("""
            /**
            * @param {Element} el
            */
            function _$$_wsmc_extract_like(el) {
                const fan_link = el.getElementsByClassName('fans_fan_lnk').item(0);
                return {
                    id: el.dataset.id,
                    name: fan_link.innerText,
                    url: fan_link.href
                }
            }
            
            const items = arguments[0].map(el => _$$_wsmc_extract_like(el));
            arguments[0].forEach(el => el.remove());
            return items;
        """, fan_rows)

        result = []

        for like_obj in like_objects:
            oid, is_group = self.parse_oid(like_obj['id'])
            result.append(AuthorDto(
                oid=oid,
                is_group=is_group,
                name=like_obj['name'],
                url=like_obj['url']
            ))

        return result

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
