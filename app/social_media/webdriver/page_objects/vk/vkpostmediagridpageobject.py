from selenium.webdriver.remote.webelement import WebElement

from .abstractvkpageobject import AbstractVkPageObject
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy


class VkPostMediaGridPageObject(AbstractVkPageObject):
    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, media_grid_element: WebElement):
        super().__init__(driver, link_strategy)
        self.media_grid_element = media_grid_element


