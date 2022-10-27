import logging
from datetime import date
from typing import Final

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from .abstractfbpageobject import AbstractFbPageObject
from ...common import date_to_local_month

logger = logging.getLogger(__name__)


class FacebookPostsFilterDialogFragment(AbstractFbPageObject):
    YEAR_INDEX: Final[int] = 0
    MONTH_INDEX: Final[int] = 1

    @staticmethod
    def get_filter_dialog_locator():
        return By.XPATH, '//div[@role="dialog"][@aria-label="Фильтры публикаций"]'

    def get_filter_dialog(self):
        return self.driver.find_element(*self.get_filter_dialog_locator())

    def get_filters_button(self):
        return self.driver.find_element(By.XPATH, '//div[@role="button"][@aria-label="Фильтры"]')

    def get_submit_button(self, dialog: WebElement):
        return dialog.find_element(By.XPATH, '//div[@role="button" and @aria-label="Готово" and @tabindex="0"]')

    def get_selectors(self):
        return self.driver.find_elements(By.XPATH, '//div[@role="combobox"]')

    def set_post_filter_year_month(self, date_to_set: date):
        logger.info(f'Setting FB filter to {date_to_set}')
        self.open_dialog()

        self._select_in_dropdown(self._open_selector(self.YEAR_INDEX), date_to_set.year.__str__())
        self._select_in_dropdown(self._open_selector(self.MONTH_INDEX),
                                 date_to_local_month(date_to_set))
        self.get_submit_button(self.get_filter_dialog()).click()

    def open_dialog(self):
        button = self.get_filters_button()
        self.scroll_into_view(button)
        button.click()

        self.get_wait().until(EC.visibility_of_element_located(self.get_filter_dialog_locator()))
        logger.debug('Dialog opened')

    def _open_selector(self, index: int):
        self.get_wait().until(lambda d: len(self.get_selectors()) > 0)
        selector = self.get_selectors()[index]
        selector.click()

        self.get_wait().until(EC.element_attribute_to_include((By.ID, selector.get_attribute('id')), 'aria-controls'))
        logger.debug('Selector opened')
        dropdown = self.driver.find_element(By.ID, selector.get_attribute('aria-controls'))
        return dropdown

    def _select_in_dropdown(self, dropdown: WebElement, value_to_select: str):
        logger.debug(f'Tying to find "{value_to_select}" in selector')
        for el in dropdown.find_elements(By.XPATH, '//div[@role="option"]'):
            if el.get_property('textContent') == value_to_select:
                el.click()
                return

        raise RuntimeError(f'Cannot find element in dropdown for value:{value_to_select}')
