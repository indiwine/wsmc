import json
import logging
from typing import Generator, List, Optional

from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos import AuthorDto
from .abstractvkpageobject import AbstractVkPageObject
from .vkpostfansboxpageobject import VkPostFansBoxPageObject
from ...exceptions import WsmcWebDriverPostLikesException
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy

logger = logging.getLogger(__name__)

class VkPostReactionsPageObject(AbstractVkPageObject):
    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, post_button_reactions_container: WebElement):
        """
        Page objects represents "like" button functionality
        @param driver:
        @param link_strategy:
        @param post_button_reactions_container: a "like" button container ('.PostButtonReactionsContainer')
        """
        super().__init__(driver, link_strategy)
        self.post_button_reactions_container = post_button_reactions_container

    @staticmethod
    def reactions_popper_locator():
        return By.CLASS_NAME, 'ReactionsMenuPopper'

    @staticmethod
    def fans_box_locator():
        return By.CLASS_NAME, 'fans_box'

    def fans_box(self):
        return self.driver.find_element(*self.fans_box_locator())

    def bottom_reactions_btn(self):
        return self.post_button_reactions_container.find_element(By.CLASS_NAME, 'PostButtonReactions')

    def bottom_action_count(self):
        return self.post_button_reactions_container.find_element(By.CLASS_NAME, 'PostBottomAction__count')

    def like_reactions(self):
        return self.post_button_reactions_container.find_elements(By.CSS_SELECTOR, '.ReactionsMenu__inner > .Reaction')

    def likes_count(self) -> int:
        item = self.bottom_reactions_btn().get_attribute('data-reaction-counts')
        if item is None:
            return 0

        count_data = json.loads(item)
        if isinstance(count_data, dict):
            return sum(count_data.values())

        if isinstance(count_data, list) and len(count_data) >= 1:
            return count_data[0]

        raise WsmcWebDriverPostLikesException(f'Likes count data does not match any known format: "{item}"')

    def open_likes_modal_and_collect(self) -> Optional[Generator[List[AuthorDto], None, None]]:
        if self.likes_count() <= 0:
            return None

        fan_box_object = self.open_likes_window()
        if not fan_box_object:
            return None

        return fan_box_object.generate_likes()

    def open_likes_window(self) -> Optional[VkPostFansBoxPageObject]:
        self.driver.scroll_into_view(self.post_button_reactions_container)
        btn_node = self.bottom_reactions_btn()
        ActionChains(self.driver).move_to_element(btn_node).perform()
        self.get_wait().until(EC.visibility_of_element_located(self.reactions_popper_locator()))

        for reaction_container in self.like_reactions():
            try:
                reaction_box = reaction_container.find_element(By.CLASS_NAME, 'ReactionTitle--withUsers')
            except NoSuchElementException:
                continue
            else:
                ActionChains(self.driver).move_to_element(reaction_container).perform()
                self.get_wait().until(EC.visibility_of(reaction_box))
                reaction_box.click()
                self.get_wait().until(EC.visibility_of_element_located(self.fans_box_locator()))
                return VkPostFansBoxPageObject(self.driver, self.link_strategy, self.fans_box())

        logger.warning('Cannot locate button to open modal window with likes at "%s"', self.driver.get_current_url_safe)

        return None
