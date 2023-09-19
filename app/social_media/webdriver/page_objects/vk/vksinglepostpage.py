from selenium.webdriver.common.by import By

from .abstractvkpageobject import AbstractVkPageObject
from .vkpostpageobject import VkPostPageObject


class VkSinglePostPage(AbstractVkPageObject):
    def get_post_node(self):
        return self.driver.find_element(By.CSS_SELECTOR, '#page_wall_posts > .post')

    def get_post_page_object(self, url) -> VkPostPageObject:
        self.navigate_to(url)
        return VkPostPageObject(self.driver, self.link_strategy, self.get_post_node())
