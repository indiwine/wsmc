from celery import shared_task, Task

from social_media.models import Suspect
from social_media.screening.screener import Screener
from .webdriver.management import collect_groups, collect_unknown_profiles, collect_profiles, do_discover_profiles


@shared_task(name='task.profile', queue='webdriver')
def perform_sm_data_collection(suspect_id: int, with_posts: bool):
    collect_profiles(suspect_id, with_posts)


@shared_task(name='task.group.webdriver', bind=True, queue='webdriver')
def collect_group_webdriver(self: Task, suspect_group_id: int):
    collect_groups(suspect_group_id, self.request.id)


@shared_task(name='task.group.common', bind=True, queue='default')
def collect_group_common(self: Task, suspect_group_id: int):
    collect_groups(suspect_group_id, self.request.id)


@shared_task(name='task.discover_profiles', bind=True, queue='default')
def discover_profiles(self: Task, suspect_place: int):
    do_discover_profiles(suspect_place, self.request.id)


@shared_task(name='task.unknown_profiles', queue='webdriver')
def perform_unknown_profiles_data_collection_task(suspect_group_id: int):
    collect_unknown_profiles(suspect_group_id)


@shared_task(name='task.screening', queue='default')
def perform_screening(suspect_id):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    screen = Screener.build(suspect)
    new_score = screen.scan()
    suspect.score = new_score
    suspect.save()
