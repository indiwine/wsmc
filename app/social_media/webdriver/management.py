import asyncio
import logging
import time
from typing import List

from asgiref.sync import sync_to_async
from pyee.base import EventEmitter

from social_media.models import Suspect, SuspectSocialMediaAccount, SuspectGroup
from social_media.social_media import SocialMediaEntities
from social_media.webdriver import Request, Agent
from .post_process_pipeline.filters.downloadpostimagesfilter import DownloadPostImagesFilter
from .post_process_pipeline.filters.persistpostimagesfilter import PersistPostImagesFilter
from .post_process_pipeline.filters.suitablepostimagesfilter import SuitablePostImagesFilter
from .post_process_pipeline.filters.vatapredictionpostimagesfilter import VataPredictionPostImagesFilter
from .post_process_pipeline.postprocesspipeline import PostProcessPipeline
from .post_process_pipeline.postprocesstask import PostProcessTask
from ..dtos.smpostdto import SmPostDto

logger = logging.getLogger(__name__)

POST_BATCH_SIZE = 50


def collect_groups(suspect_group_id: int):
    suspect_group = SuspectGroup.objects.get(id=suspect_group_id)
    collect_request = Request(
        [
            SocialMediaEntities.LOGIN,
            SocialMediaEntities.GROUP,
            SocialMediaEntities.POSTS
        ],
        suspect_group.credentials,
        suspect_group
    )

    # collect_request.load_latest = False
    # collect_request.post_limit = 1000
    agent = Agent(collect_request)
    agent.run()

    # retry_count = 0
    # while True:
    #     if retry_count >= 10:
    #         break
    #
    #     retry_count += 1
    #     agent = Agent(collect_request)
    #
    #     try:
    #         agent.run()
    #         break
    #     except WebDriverException as e:
    #         logger.error('Error while running agent', exc_info=e)
    #         agent.close_driver()
    #         time.sleep(5)


def collect_unknown_profiles(suspect_group_id: int):
    suspect_group = SuspectGroup.objects.get(id=suspect_group_id)
    collect_request = Request(
        [
            SocialMediaEntities.LOGIN,
            SocialMediaEntities.UNKNOWN_PROFILES
        ],
        suspect_group.credentials,
    )

    agent = Agent(collect_request)
    agent.run()


async def collect_and_process(suspect_id: int, with_posts: bool):
    event_emitter = EventEmitter()
    await asyncio.gather(data_processing(event_emitter), data_collection(suspect_id, with_posts, event_emitter))


@sync_to_async
def data_collection(suspect_id: int, with_posts: bool, ee: EventEmitter):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    sm_accounts = SuspectSocialMediaAccount.objects.filter(suspect=suspect)
    for sm_account in sm_accounts:
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
            agent.run()
        finally:
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
