from asgiref.sync import sync_to_async

from social_media.ai.loader import get_model
from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask


class VataPredictionPostImagesFilter(BasePostProcessFilter):
    def __init__(self):
        self.model = get_model()

    @sync_to_async
    def __call__(self, task: PostProcessTask) -> PostProcessTask:
        images = task.flatten_post_images()
        predictions = self.model.predict([img.tmpLocation for img in images])

        for i, img_predictions in enumerate(predictions):
            images[i].prediction = img_predictions

        return task
