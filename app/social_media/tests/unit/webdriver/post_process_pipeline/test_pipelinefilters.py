import asyncio
import datetime
from dataclasses import asdict
from pathlib import Path
from pprint import pprint
from typing import List

from django.test import TestCase
from faker import Faker
from faker.providers import date_time, file, internet
from unittest import skip

import social_media
from social_media.ai.models.vatapredictionitem import VataPredictionItem
from social_media.dtos.smpostdto import SmPostDto
from social_media.dtos.smpostimagedto import SmPostImageDto
from social_media.models import SmCredential, Suspect, SmProfile, SmPost, SmPostImage
from social_media.social_media.socialmediatypes import SocialMediaTypes
from social_media.webdriver.post_process_pipeline.filters.basepostprocessfilter import BasePostProcessFilter
from social_media.webdriver.post_process_pipeline.filters.downloadpostimagesfilter import DownloadPostImagesFilter
from social_media.webdriver.post_process_pipeline.filters.persistpostimagesfilter import PersistPostImagesFilter
from social_media.webdriver.post_process_pipeline.filters.suitablepostimagesfilter import SuitablePostImagesFilter
from social_media.webdriver.post_process_pipeline.filters.vatapredictionpostimagesfilter import \
    VataPredictionPostImagesFilter
from social_media.webdriver.post_process_pipeline.postprocesspipeline import PostProcessPipeline
from social_media.webdriver.post_process_pipeline.postprocesstask import PostProcessTask

IMAGES = [
    'test_imgs/russian_flag.jpg',
    'test_imgs/v.jpg',
    'test_imgs/z_and_russian.jpg',
    'test_imgs/z_colorado.jpg',
    'test_imgs/z_flag.jpg',
    'test_imgs/z_girls.jpg',
    'test_imgs/z_grafiti.jpg',
    'test_imgs/z_vihicle.jpg',
    'test_imgs/bulb.jpg',
    'test_imgs/sunset-silhouette.jpg',
]


@skip('As of now this is not a part of the future functionality')
class TestPipelineFilters(TestCase):
    _img_id = None

    def setUp(self) -> None:
        credentials = SmCredential.objects.create(user_name='test', password='test', social_media=SocialMediaTypes.VK)
        suspect = Suspect.objects.create(name='Test Suspect')
        sm_profile = SmProfile.objects.create(
            credentials=credentials,
            suspect=suspect,
            name='Test Suspect Account',
            oid='1'
        )
        post = SmPost.objects.create(
            profile=sm_profile,
            suspect=suspect,
            sm_post_id='1',
            social_media=SocialMediaTypes.VK,
            body='Test post',
            datetime=datetime.datetime.now()
        )
        img = SmPostImage.objects.create(
            post=post,
            oid='1',
        )
        self._img_id = img.id

    async def test_suitablepostimagesfilter(self):
        pipeline_filter = SuitablePostImagesFilter()
        posts, valid_results = self.generate_posts()
        task = PostProcessTask(posts)
        result = await pipeline_filter(task)
        filtered_posts = result.posts
        self.assertCountEqual(self.posts_to_dicts(valid_results), self.posts_to_dicts(filtered_posts))

    async def test_downloadpostimagesfilter(self):
        download_filter = DownloadPostImagesFilter()
        _, downloadable_items = self.generate_posts()
        task = PostProcessTask(downloadable_items)
        result = await download_filter(task)
        filtered_posts = result.posts
        for post in filtered_posts:
            for image in post.images:
                self.assertIsNotNone(image.tmpLocation)
                path_to_image = Path(image.tmpLocation)

                self.assertTrue(path_to_image.is_file(), f"'{image.tmpLocation}' is not a file")
                self.assertGreater(path_to_image.stat().st_size, 0, 'File is empty')
                path_to_image.unlink()

    async def test_vatapredictionpostimagesfilter(self):
        prediction_filter = VataPredictionPostImagesFilter()

        fake = Faker()
        fake.add_provider(date_time)
        fake.add_provider(internet)

        base_path = Path(*social_media.__path__)

        posts = [
            SmPostDto(datetime=fake.date_time(), id=5, images=[
                SmPostImageDto(oid=str(fake.random_int()),
                               id=fake.random_int(),
                               created=True,
                               url=fake.image_url(100, 100),
                               tmpLocation=base_path.joinpath(img_path).__str__()) for img_path in IMAGES
            ])]
        task = PostProcessTask(posts)
        result = await prediction_filter(task)

        filtered_posts = result.posts
        for post in filtered_posts:
            self.assertIsNotNone(post.images, 'Images are empty')
            self.assertGreater(len(post.images), 0, 'Images list are empty')
            for image in post.images:
                self.assertIsNotNone(image.prediction, 'Image prediction is none')
                self.assertEqual(type(image.prediction), list, 'Image prediction are not a list')
                for prediction_item in image.prediction:
                    self.assertIsInstance(prediction_item, VataPredictionItem)

    async def test_persistpostimagesfilter(self):
        persistent_filter = PersistPostImagesFilter()
        fake = Faker()
        fake.add_provider(date_time)

        base_path = Path(*social_media.__path__)

        post = SmPostDto(
            datetime=fake.date_time(),
            id=1,
            images=[SmPostImageDto(
                id=self._img_id,
                oid='1',
                tmpLocation=base_path.joinpath(IMAGES[0]).__str__(),
                prediction=[
                    VataPredictionItem(
                        x=1,
                        y=2,
                        width=100,
                        height=100,
                        label='z',
                        pr=0.5
                    )
                ]
            )]
        )
        task = PostProcessTask([post])
        await persistent_filter(task)
        saved_images = await SmPostImage.objects.aget(id=self._img_id)
        pprint(saved_images.prediction)
        self.assertIsNotNone(saved_images.prediction)

    async def test_pipeline(self):
        permalink = 'http://exapmle.com'
        sm = 'vk'

        class PiplineFilter1(BasePostProcessFilter):
            async def __call__(self, task: PostProcessTask) -> PostProcessTask:
                await asyncio.sleep(1)
                for post in task.posts:
                    post.permalink = permalink
                return task

        class PipelineFilter2(BasePostProcessFilter):
            async def __call__(self, task: PostProcessTask) -> PostProcessTask:
                for post in task.posts:
                    post.social_media = sm
                return task

        pipeline = PostProcessPipeline()
        pipeline.pipe(PiplineFilter1(), PipelineFilter2())
        fake = Faker()

        fake.add_provider(date_time)
        post = SmPostDto(datetime=fake.date_time(), id=1)
        test_task = PostProcessTask([post])
        result = await pipeline.execute(test_task)
        resulting_post = result.posts[0]
        self.assertEqual(permalink, resulting_post.permalink)
        self.assertEqual(sm, resulting_post.social_media)

    @staticmethod
    def posts_to_dicts(posts: List[SmPostDto]):
        return [asdict(post) for post in posts]

    @staticmethod
    def generate_posts():
        fake = Faker()

        fake.add_provider(date_time)
        fake.add_provider(file)
        post_dates = fake.date_time()

        result = [
            SmPostDto(datetime=post_dates, id=1, ),
            SmPostDto(datetime=post_dates, id=2, images=[
                SmPostImageDto(oid='1', id=1, created=False, url='https://picsum.photos/100/100'),
                SmPostImageDto(oid='2', id=2, created=True, url='https://picsum.photos/100/100')
            ]),
            SmPostDto(datetime=post_dates, id=3, images=[
                SmPostImageDto(oid='1', id=3, created=True, url='https://picsum.photos/100/100'),
                SmPostImageDto(oid='2', id=4, created=True, url='https://picsum.photos/100/100')
            ])
        ]

        valid_results = [
            SmPostDto(datetime=post_dates, id=2, images=[
                SmPostImageDto(oid='2', id=2, created=True, url='https://picsum.photos/100/100')
            ]),
            SmPostDto(datetime=post_dates, id=3, images=[
                SmPostImageDto(oid='1', id=3, created=True, url='https://picsum.photos/100/100'),
                SmPostImageDto(oid='2', id=4, created=True, url='https://picsum.photos/100/100')
            ])
        ]

        return result, valid_results
