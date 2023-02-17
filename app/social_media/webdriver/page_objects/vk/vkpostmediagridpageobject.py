import json
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from social_media.dtos.smpostimagedto import SmPostImageDto
from .abstractvkpageobject import AbstractVkPageObject
from ...exceptions import WsmcWebDriverPostImageException
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy


class VkPostMediaGridPageObject(AbstractVkPageObject):
    IMG_QUALITIES = ['w', 'z', 'y', 'x']

    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, media_grid_element: WebElement):
        super().__init__(driver, link_strategy)
        self.media_grid_element = media_grid_element

    def get_media_grid_interactive(self):
        return self.media_grid_element.find_elements(By.CLASS_NAME, 'MediaGrid__interactive')

    def extract_images(self) -> List[SmPostImageDto]:
        results = []
        for element in self.get_media_grid_interactive():
            item = self._extract_media_grid_item(element)
            if item:
                results.append(item)
        return results

    def _extract_media_grid_item(self, element: WebElement) -> Optional[SmPostImageDto]:
        item = SmPostImageDto(
            oid=element.get_attribute('data-photo-id')
        )

        img_options = element.get_attribute('data-options')
        img_options = json.loads(img_options)
        locations: dict = img_options['temp']
        img_url = None
        for quality in self.IMG_QUALITIES:
            if quality in locations:
                img_url = locations[quality]
                break

        if img_url is None:
            raise WsmcWebDriverPostImageException('Cannot find url for photo')

        item.url = img_url

        return item
