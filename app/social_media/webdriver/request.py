import logging
from typing import Optional, List, Union

from pyee import EventEmitter

from .driverbuilder import DriverBuilder, DriverBuildOptions
from .options.baseoptions import BaseOptions
from .options.vkoptions import VkOptions
from .wsmcwebdriver import WsmcWebDriver
from ..models import SuspectSocialMediaAccount, SmCredential, SuspectGroup
from ..social_media import SocialMediaEntities, SocialMediaTypes

logger = logging.getLogger(__name__)


class Request:
    _driver: Optional[WsmcWebDriver] = None
    _is_img_disabled = False

    post_limit = None
    load_latest = True
    is_retrying = False
    last_retry_success = False

    def __init__(self,
                 entities: List[SocialMediaEntities],
                 credentials: SmCredential,
                 suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup] = None,
                 ee: EventEmitter = None):

        self.entities = entities

        self.credentials = credentials

        self.suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup] = suspect_identity

        self.ee = ee

        self.options = self.build_default_options()
        self.driver_build_options = DriverBuildOptions()
        self.driver_build_options.profile_folder_name = f'chrome_cred_{credentials.id}'

    def __str__(self):
        return f'Request: "{self.credentials.social_media}", [{self.entities}]'

    @property
    def driver(self) -> WsmcWebDriver:
        if self._driver is None:
            logger.info('Building selenium driver')
            self._driver = DriverBuilder.build(self.driver_build_options)
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

    def build_default_options(self) -> BaseOptions:
        if self.get_social_media_type == SocialMediaTypes.VK:
            return VkOptions()
        elif self.get_social_media_type == SocialMediaTypes.FB:
            raise NotImplementedError('Options for fb is not implemented')
        elif self.get_social_media_type == SocialMediaTypes.OK:
            raise NotImplementedError('Options for ok is not implemented')

        raise RuntimeError(f'Unknown social media type: {self.get_social_media_type}')

    def configure_for_retry(self):
        self.last_retry_success = False
        self.is_retrying = True
        self.options.configure_for_retry()

    def mark_retry_successful(self):
        if self.is_retrying:
            self.is_retrying = False
            self.last_retry_success = True

    @property
    def was_retry_successful(self):
        return self.last_retry_success

    def close_driver(self):
        if self._driver is not None:
            self.driver.quit_safe()
            self._driver = None

    def can_process_entity(self, entity: SocialMediaEntities, has_social_media_account: bool = True) -> bool:
        return self.has_entity(entity) and (not has_social_media_account or (
            has_social_media_account and self.suspect_identity is not None))

    def has_entity(self, entity: SocialMediaEntities) -> bool:
        return entity in self.entities
