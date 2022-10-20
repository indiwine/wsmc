import logging

from .abstractscreeningmodule import AbstractScreeningModule
from social_media.exceptions import LocationRequestInvalidError
from social_media.models import SmProfile, Location, ScreeningDetail
from social_media.screening import ScreeningModules
from social_media.screening.screeningrequest import ScreeningRequest

logger = logging.getLogger(__name__)


class ProfileLocationScreener(AbstractScreeningModule):
    def handle(self, screening_request: ScreeningRequest):

        for profile in SmProfile.objects.filter(suspect=screening_request.suspect):
            check_result = self._check_profile(profile)
            screening_request.add_score(check_result['score'])
            ScreeningDetail(
                report=screening_request.report,
                content_object=profile,
                module=ScreeningModules.PROFILE_LOCATION,
                result=check_result
            ).save()

        super().handle(screening_request)

    def _check_profile(self, profile: SmProfile) -> dict:
        result = {
            'score': 0,
            'found_location': None,
            'match': []
        }
        if profile.location is not None:
            try:
                point, geolocation = Location.get_point(profile.location)
                result['found_location'] = geolocation.__str__()
                for location in Location.objects.all():
                    if location.intersects_with_point(point):
                        result['score'] += location.weight
                        result['match'].append({
                            'score': location.weight,
                            'location': location.name
                        })

            except LocationRequestInvalidError:
                logger.warning(f'Cannot find location "{profile.location}"')
                result['score'] = 1
        else:
            result['score'] = 1

        return result
