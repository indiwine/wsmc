import logging
from dataclasses import asdict
from pathlib import Path

from asgiref.sync import sync_to_async
from django.core.files import File

from social_media.models import SmPostImage
from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask

logger = logging.getLogger(__name__)


class PersistPostImagesFilter(BasePostProcessFilter):

    @sync_to_async
    def __call__(self, task: PostProcessTask) -> PostProcessTask:
        logger.debug('Persisting predictions...')
        for post in task.posts:
            for image in post.images:
                if image.prediction:
                    image_obj = SmPostImage.objects.get(id=image.id)
                    image_obj.prediction = [asdict(item) for item in image.prediction]
                    path = Path(image.tmpLocation)
                    with path.open(mode='rb') as fp:
                        image_obj.image = File(fp, name=path.name)
                        image_obj.save()
        logger.debug('Persisting predictions... Done')
        return task
