import logging
from dataclasses import asdict
from pathlib import Path

from asgiref.sync import sync_to_async
from django.core.files import File

from social_media.dtos.smpostimagedto import SmPostImageDto
from social_media.models import SmPostImage
from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask

logger = logging.getLogger(__name__)


class PersistPostImagesFilter(BasePostProcessFilter):

    async def __call__(self, task: PostProcessTask) -> PostProcessTask:
        logger.debug('Persisting predictions...')
        for post in task.posts:
            for image in post.images:
                if image.prediction:
                    await sync_to_async(self._do_save_image, thread_sensitive=False)(image)

        logger.debug('Persisting predictions... Done')
        return task

    def _do_save_image(self, image: SmPostImageDto):
        logger.debug(f'Persisting image: {image}')
        image_obj = SmPostImage.objects.get(id=image.id)
        image_obj.prediction = [asdict(item) for item in image.prediction]
        path = Path(image.tmpLocation)
        with path.open(mode='rb') as fp:
            image_obj.image = File(fp, name=path.name)
            image_obj.save()
        logger.debug(f'[DONE] Persisting image: {image}')
