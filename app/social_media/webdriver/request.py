import logging

logger = logging.getLogger(__name__)

from typing import Optional, List


from selenium.webdriver.remote.webdriver import WebDriver

from .driverbuilder import DriverBuilder
from ..models import SuspectSocialMediaAccount, SmCredentials
from ..social_media import SocialMediaEntities


class Request:
    _driver: Optional[WebDriver] = None

    def __init__(self, entities: List[SocialMediaEntities], credentials: SmCredentials, social_media_account: SuspectSocialMediaAccount = None):
        self.entities = entities
        self.credentials = credentials
        self.social_media_account: Optional[SuspectSocialMediaAccount] = social_media_account

    def __str__(self):
        return f'Request: "{self.credentials.social_media}", [{self.entities}]'

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            logger.info('Building selenium driver')
            self._driver = DriverBuilder.build()
        return self._driver

    def close_driver(self):
        if self._driver is not None:
            logger.info('Closing selenium driver')
            self._driver.quit()
            self._driver = None

    def can_process_entity(self, entity: SocialMediaEntities, has_social_media_account: bool = True) -> bool:
        return entity in self.entities and (not has_social_media_account or (has_social_media_account and self.social_media_account is not None))
