import logging

from django.db import transaction

from social_media.models import SmProfile
from ..abstractcollector import AbstractCollector
from ...exceptions import WsmcWebDriverProfileException
from ...link_builders.vk import VkLinkBuilder
from ...page_objects.vk.vkprofilepage import VkProfilePage
from ...request import Request

logger = logging.getLogger(__name__)

MAX_RETRY_COUNT = 15

CHUNK_SIZE = 10

COOLDOWN_SECONDS = 60


class VkSecondaryProfilesCollector(AbstractCollector):
    def handle(self, request: Request):
        profiles_left = True

        while profiles_left:
            profiles = SmProfile.objects \
                           .select_for_update(skip_locked=True) \
                           .filter(was_collected=False, social_media=request.get_social_media_type)[:CHUNK_SIZE]

            with transaction.atomic():
                if len(profiles) < CHUNK_SIZE:
                    profiles_left = False

                for profile in profiles:
                    logger.debug(f'Collecting profile {profile}')
                    profile_page_object = VkProfilePage(request.driver, VkLinkBuilder.build(profile.id_url()))
                    profile_dto = profile_page_object.retry_action(
                        action=lambda: profile_page_object.collect_profile(),
                        cooldown_time=COOLDOWN_SECONDS,
                        additional_exceptions=[WsmcWebDriverProfileException],
                        max_retry_count=MAX_RETRY_COUNT
                    )

                    SmProfile.objects.filter(id=profile.id).update(was_collected=True,
                                                                   **self.as_dict_for_model(profile_dto))
                    profile = SmProfile.objects.get(id=profile.id)
                    if profile.identify_location():
                        profile.save()
            request.mark_retry_successful()

        return super().handle(request)
