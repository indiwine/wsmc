import logging
from datetime import date
from typing import Final

logger = logging.getLogger(__name__)

from selenium.webdriver.remote.webelement import WebElement

from ..abstrtactpageobject import AbstractPageObject
from ...common import date_to_local_month
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class FacebookPostsFilterDialogFragment(AbstractPageObject):
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
        return dialog.find_element(By.XPATH, '//div[@role="button"][@aria-label="Готово"]')

    def get_selectors(self, dialog: WebElement):
        return dialog.find_elements(By.XPATH, '//div[@role="combobox"]')

    def set_post_filter_year_month(self, date_to_set: date):
        self.open_dialog()
        dialog_element = self.get_filter_dialog()
        self._select_in_dropdown(self._open_selector(dialog_element, self.YEAR_INDEX), date_to_set.year.__str__())
        self._select_in_dropdown(self._open_selector(dialog_element, self.MONTH_INDEX),
                                 date_to_local_month(date_to_set))
        self.get_submit_button(dialog_element).click()

    def open_dialog(self):
        self.get_filters_button().click()
        self.get_wait().until(EC.presence_of_element_located(self.get_filter_dialog_locator()))

    def _open_selector(self, dialog: WebElement, index: int):
        selector = self.get_selectors(dialog)[index]
        selector.click()
        self.get_wait().until(EC.element_attribute_to_include(selector, 'aria-controls'))
        dropdown = self.driver.find_element(By.ID, selector.get_attribute('aria-controls'))
        return dropdown

    def _select_in_dropdown(self, dropdown: WebElement, value_to_select: str):
        for el in dropdown.find_elements(By.XPATH, '//div[@role="option"]'):
            if el.get_property('textContent') == value_to_select:
                el.click()
                return

        raise RuntimeError(f'Cannot find element in dropdown for value:{value_to_select}')
