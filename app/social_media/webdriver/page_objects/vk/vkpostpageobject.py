import itertools
import logging
from datetime import datetime
from typing import Tuple, List, Optional, Generator

from django.utils import timezone
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from social_media.dtos import SmPostDto, AuthorDto, SmPostImageDto
from social_media.social_media import SocialMediaTypes
from .abstractvkpageobject import AbstractVkPageObject
from .vkpostcontentpageobject import VkPostContentPageObject
from .vkpostreactionspageobject import VkPostReactionsPageObject
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

    def post_header_author_link(self):
        return self.post_node.find_element(By.CSS_SELECTOR, '.PostHeaderTitle .PostHeaderTitle__authorLink')

    def post_bottom_reactions_container(self):
        return self.post_node.find_element(By.CLASS_NAME, 'PostButtonReactionsContainer')

    def collect(self) -> SmPostDto:
        self.driver.scroll_into_view(self.post_node)
        logger.debug('Collecting post')
        dto = SmPostDto(
            datetime=self.get_post_time(),
            sm_post_id=self.get_post_id(),
            social_media=SocialMediaTypes.VK.value,
            permalink=self.get_permalink(),
            author=self.get_post_author()
        )

        dto.body, dto.images = self.get_post_body_and_images()

        return dto

    def collect_likes(self) -> Optional[Generator[List[AuthorDto], None, None]]:
        return self.get_post_reactions_object().open_likes_modal_and_collect()

    def collect_likes_flat(self) -> Optional[List[AuthorDto]]:
        likes_gen = self.collect_likes()
        if not likes_gen:
            return None

        return list(itertools.chain(*likes_gen))

    def get_post_author(self):
        author_header = self.post_header_author_link()
        oid, is_group = self.parse_oid(author_header.get_attribute('data-from-id'))

        return AuthorDto(
            oid=oid,
            name=author_header.get_property('innerText'),
            url=author_header.get_attribute('href'),
            is_group=is_group
        )

    def get_post_content_object(self) -> VkPostContentPageObject:
        return VkPostContentPageObject(self.driver, self.link_strategy, self.wall_text())

    def get_post_reactions_object(self) -> VkPostReactionsPageObject:
        return VkPostReactionsPageObject(self.driver, self.link_strategy, self.post_bottom_reactions_container())

    def get_post_body_and_images(self) -> Tuple[str, Optional[List[SmPostImageDto]]]:
        images_result = None

        post_content = self.get_post_content_object()
        media_grid = post_content.get_media_grid_page_object()

        if media_grid:
            images = media_grid.extract_images()
            if len(images) > 0:
                images_result = images

        return post_content.to_text(), images_result

    def get_post_time(self):
        post_date_element = self.post_date()
        try:
            sub_element = self.post_date().find_element(By.CSS_SELECTOR, '[time]')
            time_attr = sub_element.get_attribute('time')

            if time_attr:
                logger.debug(f'post time found using timestamp')
                return datetime.fromtimestamp(int(time_attr), tz=timezone.get_current_timezone())
        except NoSuchElementException:
            pass

        logger.debug(f'Processing relative post time')
        return date_time_parse(post_date_element.get_attribute('textContent'))

    def get_post_id(self) -> str:
        return self.post_node.get_attribute('data-post-id')

    def get_permalink(self) -> str:
        return self.post_link().get_attribute('href')
