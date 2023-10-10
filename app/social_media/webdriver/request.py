import logging
from typing import Optional, List, Union, TypeVar, Generic

from pyee import EventEmitter

from .driverbuilder import DriverBuilder, DriverBuildOptions
from .options.baseoptions import BaseOptions
from .options.okoptions import OkOptions
from .options.vkoptions import VkOptions
from .wsmcwebdriver import WsmcWebDriver
from ..models import SuspectSocialMediaAccount, SmCredential, SuspectGroup, SuspectPlace
from ..social_media import SocialMediaActions, SocialMediaTypes

logger = logging.getLogger(__name__)

REQUEST_DATA_TYPE = TypeVar('REQUEST_DATA_TYPE')


class Request(Generic[REQUEST_DATA_TYPE]):
    """
    Request class represents single request to social media website. Contains all necessary data to process request,
    such as social media credentials, suspect identity, request options, etc.
    """

    data: REQUEST_DATA_TYPE | None
    """
    Custom data for request.
    This property is used to pass data between collectors.
    If used must be declared in Generic type
    """

    _driver: WsmcWebDriver | None
    """
    Selenium driver instance
    @todo Move driver building to separate class, so the request will not be responsible for driver building
    """

    driver_build_options: DriverBuildOptions
    """
    Selenium driver options
    @todo Move driver building to separate class, so the request will not be responsible for driver building
    """

    is_retrying: bool
    """
    Indicates if request is in the state of retrying
    """
    last_retry_success: bool
    """
    Indicates if last retry was successful
    """

    options: BaseOptions
    """
    Request options (depends on social media type)
    """

    def __init__(self,
                 actions: List[SocialMediaActions],
                 credentials: SmCredential,
                 suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup, SuspectPlace] = None,
                 ee: EventEmitter = None
                 ):
        """
        Request constructor
        @note: Not all collectors use selenium driver, so this property should be used with caution
        @param actions: list of actions to perform
        @param credentials: social media credentials to use (mostly for login)
        @param suspect_identity: suspect(ish) identity to process
        @param ee: reserved for future use
        """

        # Default values
        self._driver = None
        self.is_retrying = False
        self.last_retry_success = False
        self.data: Optional[REQUEST_DATA_TYPE] = None

        # Request data
        self._actions = actions
        self.credentials = credentials
        self.suspect_identity: Union[SuspectSocialMediaAccount, SuspectGroup, SuspectPlace] = suspect_identity

        # Event emitter (if any)
        self.ee = ee

        # Options
        self.options = self.build_default_options()
        self.driver_build_options = DriverBuildOptions()
        self.driver_build_options.profile_folder_name = f'chrome_cred_{credentials.id}'

    def __str__(self):
        return f'Request: "{self.credentials.social_media}", [{self._actions}]'

    @property
    def driver(self) -> WsmcWebDriver:
        """
        Get selenium driver

        Use this property to get selenium driver instance or reuse existing one

        @note: Not all collectors use selenium driver, so this property should be used with caution
        @todo Move driver building to separate class, so the request will not be responsible for driver building
        @return:
        """
        if not self.has_driver:
            logger.info('Building selenium driver')
            self._driver = DriverBuilder.build(self.driver_build_options)
        return self._driver

    @property
    def has_driver(self) -> bool:
        """
        Determine if request has selenium driver instance started
        @return:
        """
        return self._driver is not None

    @property
    def is_group_request(self):
        """
        Determine if request is group request (i.e. suspect identity is group)

        @raise RuntimeError: if suspect identity is not set
        @return:
        """
        if self.has_suspend_identity is False:
            raise RuntimeError(f'Cannot determine "is_group_request" since `suspect_identity` is empty')
        return isinstance(self.suspect_identity, SuspectGroup)

    @property
    def is_place_request(self):
        """
        Determine if request is place request (i.e. suspect identity is place)

        @raise RuntimeError: if suspect identity is not set
        @return:
        """
        if self.has_suspend_identity is False:
            raise RuntimeError(f'Cannot determine "is_place_request" since `suspect_identity` is empty')
        return isinstance(self.suspect_identity, SuspectPlace)

    @property
    def is_account_request(self):
        """
        Determine if request is account request (i.e. suspect identity is account)

        @raise RuntimeError: if suspect identity is not set
        @return:
        """
        if self.has_suspend_identity is False:
            raise RuntimeError(f'Cannot determine "is_account_request" since `suspect_identity` is empty')
        return isinstance(self.suspect_identity, SuspectSocialMediaAccount)

    @property
    def has_suspend_identity(self):
        """
        Determine if request has suspect identity set
        @return:
        """
        return self.suspect_identity is not None

    @property
    def target_url(self) -> str:
        """
        Get target url for request
        @raise RuntimeError: if suspect identity is not set
        @return:
        """
        if self.has_suspend_identity is False:
            raise RuntimeError(f'Cannot determine "target_url" since `suspect_identity` is empty')

        if isinstance(self.suspect_identity, SuspectGroup):
            return self.suspect_identity.url

        return self.suspect_identity.link

    @property
    def get_social_media_type(self):
        return self.credentials.social_media

    def build_default_options(self) -> BaseOptions:
        """
        Build default options for request
        @return:
        """
        if self.get_social_media_type == SocialMediaTypes.VK:
            return VkOptions()
        elif self.get_social_media_type == SocialMediaTypes.FB:
            raise NotImplementedError('Options for fb is not implemented')
        elif self.get_social_media_type == SocialMediaTypes.OK:
            return OkOptions()

        raise RuntimeError(f'Unknown social media type: {self.get_social_media_type}')

    def configure_for_retry(self):
        """
        Configure request for retrying
        @return:
        """
        self.last_retry_success = False
        self.is_retrying = True
        self.options.configure_for_retry()

    def mark_retry_successful(self):
        """
        Mark request as successful after retry
        @return:
        """
        if self.is_retrying:
            self.is_retrying = False
            self.last_retry_success = True

    @property
    def was_retry_successful(self):
        """
        Determine if last retry was successful
        @return:
        """
        return self.last_retry_success

    def close_driver(self):
        """
        Close selenium driver (if any)
        @todo Move driver building to separate class, so the request will not be responsible for driver building
        @return:
        """
        if self._driver is not None:
            self.driver.quit_safe()
            self._driver = None

    def can_process_entity(self, entity: SocialMediaActions, has_social_media_account: bool = True) -> bool:
        """
        Determine if request can process given entity
        @deprecated Not necessary anymore, since we have more elaborate pipe building
        @param entity:
        @param has_social_media_account:
        @return:
        """
        return self.has_action_assigned(entity) and (not has_social_media_account or (
            has_social_media_account and self.suspect_identity is not None))

    def has_action_assigned(self, action: SocialMediaActions) -> bool:
        """
        Determine if request has given entity to process
        @param action:
        @return:
        """
        return action in self._actions
