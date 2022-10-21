import dateparser
from typing import Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from social_media.dtos.smpostdto import SmPostDto
from social_media.social_media import SocialMediaTypes
from .abstractvkpageobject import AbstractVkPageObject


class VkProfileWallPage(AbstractVkPageObject):

    def posts(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '#page_wall_posts > .post')

    def collect_posts(self) -> Generator[SmPostDto, None, None]:
        self.get_wait().until(EC.presence_of_element_located((By.ID, 'page_wall_posts')))

        for post_node in self.posts():
            yield self._process_post_node(post_node)

    def _process_post_node(self, node: WebElement) -> SmPostDto:
        post_date = dateparser.parse(node.find_element(By.CLASS_NAME, 'post_date').get_attribute('textContent'))
        dto = SmPostDto(sm_post_id=node.get_attribute('data-post-id'),
                        datetime=post_date,
                        social_media=SocialMediaTypes.VK.value
                        )

        dto.permalink = node.find_element(By.CLASS_NAME, 'post_link').get_attribute('href')
        dto.body = node.find_element(By.CLASS_NAME, 'wall_text').get_attribute('textContent')
        return dto
