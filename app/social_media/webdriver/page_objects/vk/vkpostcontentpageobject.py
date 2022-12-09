from typing import Optional, Callable

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .abstractvkpageobject import AbstractVkPageObject
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy


class VkPostContentPageObject(AbstractVkPageObject):
    copy_quote: Optional[WebElement] = None

    def get_copy_quote(self):
        return self.wall_text_node.find_element(By.CSS_SELECTOR, ':scope > .copy_quote')

    def get_wall_post_cont(self):
        return self.wall_text_node.find_element(By.CLASS_NAME, 'wall_post_cont')

    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, wall_text_node: WebElement):
        super().__init__(driver, link_strategy)
        self.wall_text_node = wall_text_node

        try:
            self.copy_quote = self.get_copy_quote()
        except NoSuchElementException:
            pass

    @staticmethod
    def _try_find(cb: Callable[[], str]) -> str:
        try:
            return cb().strip()
        except NoSuchElementException:
            return ''

    def to_text(self) -> Optional[str]:
        self._click_more_button()
        try:
            self.wall_text_node.find_element(By.ID, 'wpt211831788_417')
            pass
        except NoSuchElementException:
            pass

        contents = [self.get_wall_post_cont()]
        if self.copy_quote:
            contents.append(self.copy_quote)
            try:
                sub_repost = self.copy_quote.find_element(By.CLASS_NAME, 'copy_quote')
                contents.append(sub_repost)
            except NoSuchElementException:
                pass

        result = ''
        nl = '\n'

        for node in contents:
            # repost author
            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'copy_post_author').get_attribute('textContent')) + nl

            # Post itself
            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'wall_post_text').get_attribute('innerText')) + nl

            # Group Sharing
            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'page_group_info').get_attribute('innerText')) + nl

            # So called "Poster"
            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'poster__text').get_attribute('innerText')) + nl

            # Video title
            result += self._try_find(
                lambda: node.find_element(By.CSS_SELECTOR, '.media_desc > .lnk > .a').get_attribute('textContent')) + nl

            # Links to outside resources
            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'thumbed_link__title').get_attribute('textContent')) + nl

            result += self._try_find(
                lambda: node.find_element(By.CLASS_NAME, 'media_link__info').get_attribute('textContent')) + nl

        result = result.strip()
        if len(result) == 0:
            return None

        return result

    def _click_more_button(self):
        self.driver.execute_script("""
        var body_node = arguments[0]
        body_node.getElementsByClassName('wall_post_more').forEach(el => el.click())
        body_node.getElementsByClassName('PostTextMore').forEach(el => el.click())
        body_node.getElementsByClassName('wall_copy_more').forEach(el => el.click())
        """, self.wall_text_node)
