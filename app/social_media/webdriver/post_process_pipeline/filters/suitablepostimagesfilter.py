import logging
from dataclasses import replace

from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask

logger = logging.getLogger(__name__)


class SuitablePostImagesFilter(BasePostProcessFilter):

    async def __call__(self, task: PostProcessTask) -> PostProcessTask:
        logger.debug('Filtering suitable images...')
        cleaned_list = []

        for post in task.posts:
            if post.images:
                new_images = list(filter(lambda image: image.created, post.images))
                if new_images:
                    post_copy = replace(post)
                    post_copy.images = new_images
                    cleaned_list.append(post_copy)

        task.posts = cleaned_list
        logger.debug('Filtering suitable images... Done')
        return task
