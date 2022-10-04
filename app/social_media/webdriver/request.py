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

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            self._driver = DriverBuilder.build()
        return self._driver

    def close_driver(self):
        if self._driver is not None:
            self._driver.quit()
            self._driver = None
