import logging
from typing import Optional, List, Union

from pyee import EventEmitter

from selenium.webdriver.remote.webdriver import WebDriver
from seleniumwire.webdriver import Remote
from .driverbuilder import DriverBuilder
from ..models import SuspectSocialMediaAccount, SmCredential, SuspectGroup
from ..social_media import SocialMediaEntities

logger = logging.getLogger(__name__)


class Request:
    _driver: Optional[Remote] = None
    _is_img_disabled = False

    post_limit = None
    load_latest = True

    def __init__(self,
                 entities: List[SocialMediaEntities],
                 credentials: SmCredential,
                 suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup] = None,
                 ee: EventEmitter = None):

        self.entities = entities

        self.credentials = credentials

        self.suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup] = suspect_identity

        self.ee = ee

    def __str__(self):
        return f'Request: "{self.credentials.social_media}", [{self.entities}]'

    @property
    def driver(self) -> Remote:
        if self._driver is None:
            logger.info('Building selenium driver')
            self._driver = DriverBuilder.build()
        return self._driver

    @property
    def is_group_request(self):
        if self.suspect_identity is None:
            raise RuntimeError(f'Cannot determine "is_group_request" since `suspect_identity` is empty')
        return isinstance(self.suspect_identity, SuspectGroup)

    @property
    def target_url(self) -> str:
        if isinstance(self.suspect_identity, SuspectGroup):
            return self.suspect_identity.url

        return self.suspect_identity.link

    @property
    def get_social_media_type(self):
        return self.credentials.social_media

    def disable_images(self):

        if self._is_img_disabled:
            return

        self._is_img_disabled = True

        def interceptor(request):
            # Block PNG, JPEG and GIF images
            logger.info(f'Interceptor: {request.path}')
            if request.path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                request.abort()

        self._driver.request_interceptor = interceptor

    def enable_images(self):
        if not self._is_img_disabled:
            return

        self._is_img_disabled = False
        self._driver.request_interceptor = None

    def close_driver(self):
        if self._driver is not None:
            logger.info('Closing selenium driver')
            try:
                self._driver.quit()
            except Exception as e:
                logger.error('Error while quiting webdriver', exc_info=e)
            finally:
                self._driver = None

    def can_process_entity(self, entity: SocialMediaEntities, has_social_media_account: bool = True) -> bool:
        return self.has_entity(entity) and (not has_social_media_account or (
            has_social_media_account and self.suspect_identity is not None))

    def has_entity(self, entity: SocialMediaEntities) -> bool:
        return entity in self.entities
