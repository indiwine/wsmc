import asyncio

from celery import shared_task
from django.conf import settings

from social_media.models import Suspect
from social_media.screening.screener import Screener
from .webdriver.management import collect_and_process, collect_groups, collect_unknown_profiles


@shared_task
def perform_sm_data_collection(suspect_id: int, with_posts: bool):
    asyncio.run(collect_and_process(suspect_id, with_posts), debug=settings.DEBUG)


@shared_task
def perform_group_data_collection_task(suspect_group_id: int):
    collect_groups(suspect_group_id) @ shared_task


@shared_task
def perform_unknown_profiles_data_collection_task(suspect_group_id: int):
    collect_unknown_profiles(suspect_group_id)


@shared_task
def perform_screening(suspect_id):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    screen = Screener.build(suspect)
    new_score = screen.scan()
    suspect.score = new_score
    suspect.save()
