import asyncio
import logging
import mimetypes
import tempfile

import aiohttp
from fake_useragent import UserAgent

from social_media.dtos.smpostimagedto import SmPostImageDto
from .basepostprocessfilter import BasePostProcessFilter
from ..postprocesstask import PostProcessTask
from ...common import chunks_list

logger = logging.getLogger(__name__)

BATCH_SIZE = 4


class DownloadPostImagesFilter(BasePostProcessFilter):
    def __init__(self):
        self.ua = UserAgent().random

    async def __call__(self, task: PostProcessTask) -> PostProcessTask:
        logger.info('Start image downloading...')

        images = task.flatten_post_images()

        for images_chunk in list(chunks_list(images, BATCH_SIZE)):
            await asyncio.gather(*[self._download_image(image) for image in images_chunk])

        logger.info('Downloading done')
        return task

    async def _download_image(self, image: SmPostImageDto):
        logger.debug(f'Downloading image: {image}')
        async with aiohttp.ClientSession(headers={'user-agen': self.ua}) as session:
            async with session.get(image.url) as r:
                with tempfile.NamedTemporaryFile(suffix=mimetypes.guess_extension(r.headers.get('content-type'))) as fd:
                    async for chunk in r.content.iter_chunked(1000):
                        fd.write(chunk)

                    fd.close()
                    image.tmpLocation = fd.name
                    logger.debug(f'Downloading done: {image}')
