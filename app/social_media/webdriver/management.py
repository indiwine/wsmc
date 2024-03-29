import asyncio
import logging
import time
from typing import List, Optional

from asgiref.sync import sync_to_async, async_to_sync
from pyee.base import EventEmitter

from social_media.models import Suspect, SuspectSocialMediaAccount, SuspectGroup
from social_media.social_media import SocialMediaEntities
from social_media.webdriver import  Agent
from .post_process_pipeline.filters.downloadpostimagesfilter import DownloadPostImagesFilter
from .post_process_pipeline.filters.persistpostimagesfilter import PersistPostImagesFilter
from .post_process_pipeline.filters.suitablepostimagesfilter import SuitablePostImagesFilter
from .post_process_pipeline.filters.vatapredictionpostimagesfilter import VataPredictionPostImagesFilter
from .post_process_pipeline.postprocesspipeline import PostProcessPipeline
from .post_process_pipeline.postprocesstask import PostProcessTask
from .request import Request
from ..dtos.smpostdto import SmPostDto

logger = logging.getLogger(__name__)

POST_BATCH_SIZE = 50

@async_to_sync
async def collect_groups(suspect_group_id: int, task_id: str):
    suspect_group = await SuspectGroup.objects.aget(id=suspect_group_id)
    credentials = await suspect_group.afetch_next_credential()
    collect_request = Request(
        [
            SocialMediaEntities.LOGIN,
            SocialMediaEntities.GROUP,
            SocialMediaEntities.POSTS
        ],
        credentials,
        suspect_group
    )

    agent = Agent(collect_request, task_id)
    await agent.run()

@async_to_sync
async def collect_unknown_profiles(suspect_group_id: int):
    suspect_group = SuspectGroup.objects.get(id=suspect_group_id)
    collect_request = Request(
        [
            SocialMediaEntities.LOGIN,
            SocialMediaEntities.UNKNOWN_PROFILES
        ],
        suspect_group.credentials,
    )

    agent = Agent(collect_request)
    await agent.run()

@async_to_sync()
async def collect_and_process(suspect_id: int, with_posts: bool):
    event_emitter = EventEmitter()
    await asyncio.gather(data_processing(event_emitter), post_data_collection(suspect_id, with_posts, event_emitter))

@async_to_sync
async def collect_profiles(suspect_id: int, with_posts: bool):
    await post_data_collection(suspect_id, with_posts)

async def post_data_collection(suspect_id: int, with_posts: bool, ee: Optional[EventEmitter] = None):
    suspect: Suspect = await Suspect.objects.aget(id=suspect_id)
    async for sm_account in SuspectSocialMediaAccount.objects.select_related('credentials').filter(suspect=suspect):
        entities = [SocialMediaEntities.LOGIN, SocialMediaEntities.PROFILE]
        if with_posts:
            entities.append(SocialMediaEntities.POSTS)

        collect_request = Request(
            entities,
            sm_account.credentials,
            sm_account,
            ee=ee
        )

        agent = Agent(collect_request)
        try:
            await agent.run()
        finally:
            if ee:
                ee.emit('finish')



async def data_processing(ee: EventEmitter):
    pipeline = PostProcessPipeline()
    pipeline.pipe(SuitablePostImagesFilter(),
                  DownloadPostImagesFilter(),
                  VataPredictionPostImagesFilter(),
                  PersistPostImagesFilter())

    finish = False
    posts: List[SmPostDto] = []

    def count_new_images_in_posts():
        i = 0
        for post in posts:
            if post.images:
                i += len(list(filter(lambda image: image.created, post.images)))
        return i

    @ee.on('post')
    def post_handler(post: SmPostDto):
        if post.images:
            posts.append(post)

    @ee.on('finish')
    def finish_handler():
        logger.info('Pipeline: Finished signal received')
        nonlocal finish
        finish = True

    while True:
        new_image_count = count_new_images_in_posts()

        if finish or (not finish and new_image_count >= POST_BATCH_SIZE):
            if new_image_count == 0:
                return
            t0 = time.perf_counter()
            logger.info('Activating pipeline...')

            freeze_posts = posts.copy()
            for item in freeze_posts:
                posts.remove(item)

            await pipeline.execute(PostProcessTask(posts=freeze_posts))

            logger.info(f'Pipeline finished, took: {time.perf_counter() - t0}')
        else:
            await asyncio.sleep(0.25)
