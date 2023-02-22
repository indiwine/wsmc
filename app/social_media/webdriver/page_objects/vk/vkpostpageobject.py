import json
import logging
from dataclasses import asdict

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media import SocialMediaTypes
from .abstractvkpageobject import AbstractVkPageObject
from .vkpostcontentpageobject import VkPostContentPageObject
from ...common import date_time_parse
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy

logger = logging.getLogger(__name__)


class VkPostPageObject(AbstractVkPageObject):
    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy, post_node: WebElement):
        super().__init__(driver, link_strategy)
        self.post_node = post_node

    def wall_text(self):
        return self.post_node.find_element(By.CLASS_NAME, 'wall_text')

    def post_date(self):
        return self.post_node.find_element(By.CSS_SELECTOR, 'time.PostHeaderSubtitle__item')

    def post_link(self):
        return self.post_node.find_element(By.CSS_SELECTOR, 'a.PostHeaderSubtitle__link')

    def collect(self) -> SmPostDto:
        dto = SmPostDto(
            datetime=self._get_post_time(),
            sm_post_id=self._get_post_id(),
            social_media=SocialMediaTypes.VK.value,
            permalink=self._get_permalink()
        )

        post_content = VkPostContentPageObject(self.driver, self.link_strategy, self.wall_text())

        media_grid = post_content.get_media_grid_page_object()
        if media_grid:
            images = media_grid.extract_images()
            if len(images) > 0:
                dto.images = images

        dto.body = post_content.to_text()
        # logger.info(f'VK post found: {json.dumps(asdict(dto), indent=2, ensure_ascii=False, default=str)}')
        return dto

    def _get_post_time(self):
        return date_time_parse(self.post_date().get_attribute('textContent'))

    def _get_post_id(self) -> str:
        return self.post_node.get_attribute('data-post-id')

    def _get_permalink(self) -> str:
        return self.post_link().get_attribute('href')
