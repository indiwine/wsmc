import json

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from .abstractvkpageobject import AbstractVkPageObject
from .vkpostfansboxpageobject import VkPostFansBoxPageObject
from ...exceptions import WsmcWebDriverPostLikesException
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy


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

    def like_reaction(self):
        return self.post_button_reactions_container.find_element(By.CSS_SELECTOR, '.ReactionsMenu__inner > .Reaction')

    def likes_count(self) -> int:
        item = self.bottom_reactions_btn().get_attribute('data-reaction-counts')
        count_data = json.loads(item)
        if isinstance(count_data, dict) and '0' in count_data:
            return count_data['0']

        if isinstance(count_data, list) and len(count_data) >= 1:
            return count_data[0]

        raise WsmcWebDriverPostLikesException(f'Likes count data does not match any known format: "{item}"')

    def collect_likes(self):
        if self.likes_count() <= 0:
            return None

        fan_box_object = self.open_likes_window()
        return fan_box_object.collect_likes()

    def open_likes_window(self) -> VkPostFansBoxPageObject:
        btn_node = self.bottom_reactions_btn()
        self.scroll_into_view(btn_node)
        ActionChains(self.driver).move_to_element(btn_node).perform()
        self.get_wait().until(EC.visibility_of_element_located(self.reactions_popper_locator()))

        reaction_container = self.like_reaction()
        reaction_box = reaction_container.find_element(By.CLASS_NAME, 'ReactionTitle--withUsers')

        ActionChains(self.driver).move_to_element(reaction_container).perform()
        self.get_wait().until(EC.visibility_of(reaction_box))
        reaction_box.click()
        self.get_wait().until(EC.visibility_of_element_located(self.fans_box_locator()))
        return VkPostFansBoxPageObject(self.driver, self.link_strategy, self.fans_box())
