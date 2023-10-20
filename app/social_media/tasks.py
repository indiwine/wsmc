from celery import shared_task, Task

from social_media.models import Suspect
from social_media.screening.screener import Screener
from .webdriver.exceptions import WsmcCeleryRetryException
from .webdriver.management import collect_groups, collect_profiles, do_discover_profiles


def retry_wrapper(task: Task, func: callable):
    """
    Wraps a function with a try-except block that will retry the task if an exception is raised

    This is basically a workaround for the fact that Celery does not support retrying tasks from within a task
    in case of async tasks
    @param task:
    @param func:
    @return:
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WsmcCeleryRetryException as e:
            task.retry(countdown=e.countdown, max_retries=e.max_retries, exc=e.exc)

    return wrapper


@shared_task(name='task.profile', bind=True, queue='webdriver', max_retries=5)
def perform_sm_data_collection(self: Task, suspect_id: int, with_posts: bool):
    collect_profiles(suspect_id, with_posts, self)


@shared_task(name='task.group.webdriver', bind=True, queue='webdriver', max_retries=5)
def collect_group_webdriver(self: Task, suspect_group_id: int):
    retry_wrapper(self, collect_groups)(suspect_group_id, self)


@shared_task(name='task.group.common', bind=True, queue='default', max_retries=5)
def collect_group_common(self: Task, suspect_group_id: int):
    collect_groups(suspect_group_id, self)


@shared_task(name='task.discover_profiles', bind=True, queue='default', max_retries=5)
def discover_profiles(self: Task, suspect_place: int):
    do_discover_profiles(suspect_place, self)


@shared_task(name='task.screening', queue='default')
def perform_screening(suspect_id):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    screen = Screener.build(suspect)
    new_score = screen.scan()
    suspect.score = new_score
    suspect.save()
