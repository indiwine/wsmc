import json
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from social_media.dtos.smpostimagedto import SmPostImageDto
from .abstractvkpageobject import AbstractVkPageObject
from ...exceptions import WsmcWebDriverPostImageException
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy

IMG_QUALITIES = ['w', 'z', 'y', 'x']


class VkPostMediaGridPageObject(AbstractVkPageObject):
    """Page object represents media grid item in the vk post"""

    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, media_grid_element: WebElement):
        super().__init__(driver, link_strategy)
        self.media_grid_element = media_grid_element

    def get_media_grid_interactive(self) -> List[WebElement]:
        """
        @return: list of "interactive elements"
        """
        return self.media_grid_element.find_elements(By.CSS_SELECTOR, '.MediaGrid__interactive[data-photo-id]')

    def extract_images(self) -> List[SmPostImageDto]:
        """
        Extract images from post
        @return: list of image DTOs
        """
        return [self._extract_media_grid_item(item) for item in self.get_media_grid_interactive() if item is not None]

    @staticmethod
    def _extract_media_grid_item(element: WebElement) -> Optional[SmPostImageDto]:
        oid = element.get_attribute('data-photo-id')

        img_options = element.get_attribute('data-options')
        img_options = json.loads(img_options)
        locations: dict = img_options['temp']
        img_url = None
        for quality in IMG_QUALITIES:
            if quality in locations:
                img_url = locations[quality]
                break

        if img_url is None:
            raise WsmcWebDriverPostImageException('Cannot find url for photo')

        item = SmPostImageDto(
            oid=oid,
            url=img_url
        )

        return item
