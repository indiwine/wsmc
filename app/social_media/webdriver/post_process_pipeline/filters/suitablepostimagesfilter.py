import logging
from dataclasses import replace

from asgiref.sync import sync_to_async

from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask

logger = logging.getLogger(__name__)


class SuitablePostImagesFilter(BasePostProcessFilter):

    @sync_to_async
    def __call__(self, task: PostProcessTask) -> PostProcessTask:
        logger.debug('Filtering suitable images...')
        cleaned_list = []

        for post in task.posts:
            new_images = list(filter(lambda image: image.created, post.images))
            if new_images:
                post_copy = replace(post)
                post_copy.images = new_images

        task.posts = cleaned_list
        logger.debug('Filtering suitable images... Done')
        return task
