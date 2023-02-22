from typing import List

from social_media.dtos.smpostdto import SmPostDto
from social_media.dtos.smpostimagedto import SmPostImageDto


class PostProcessTask:
    def __init__(self, posts: List[SmPostDto]):
        self.posts = posts

    def flatten_post_images(self) -> List[SmPostImageDto]:
        return [image for post in self.posts for image in post.images if post.images]
