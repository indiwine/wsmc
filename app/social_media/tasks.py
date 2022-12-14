from celery import shared_task

from social_media.models import Suspect, SuspectSocialMediaAccount
from social_media.screening.screener import Screener
from social_media.social_media import SocialMediaEntities
from social_media.webdriver import Request, Agent


@shared_task
def perform_sm_data_collection(suspect_id: int, with_posts: bool):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    sm_accounts = SuspectSocialMediaAccount.objects.filter(suspect=suspect)
    for sm_account in sm_accounts:
        entities = [SocialMediaEntities.LOGIN, SocialMediaEntities.PROFILE]
        if with_posts:
            entities.append(SocialMediaEntities.POSTS)

        collect_request = Request(
            entities,
            sm_account.credentials,
            sm_account
        )
        agent = Agent(collect_request)
        agent.run()


@shared_task
def perform_screening(suspect_id):
    suspect: Suspect = Suspect.objects.get(id=suspect_id)
    screen = Screener.build(suspect)
    new_score = screen.scan()
    suspect.score = new_score
    suspect.save()
