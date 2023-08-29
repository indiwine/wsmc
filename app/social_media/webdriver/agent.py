import logging
import time
from typing import Optional

from selenium.common import NoSuchWindowException, WebDriverException

from .collectors import Collector
from .collectors.fb import FbLoginCollector, FbProfileCollector, FbPostsCollector
from .collectors.ok import OkSeleniumLoginCollector, OkSeleniumProfileCollector, OkSeleniumPostsCollector
from .collectors.vk import VkLoginCollector, VkProfileCollector, VkPostsCollector, VkSecondaryProfilesCollector, \
    VkGroupCollector
from .exceptions import WscmWebdriverRetryFailedException, WsmcWebDriverLoginError
from .request import Request
from ..social_media import SocialMediaTypes, SocialMediaEntities

logger = logging.getLogger(__name__)


class Agent:

    def __init__(self, request: Request, task_id: Optional[str] = None):

        self.request = request
        self.task_id = task_id
        logger.info(f'Agent created for {request}')

    def _get_screenshot_prefix(self, attempt: int) -> str:
        result = f'agent_error_attempt_{attempt}'
        if self.task_id:
            result = f'{self.task_id}__{result}'
        return result

    def run(self, max_retries: int = 5, base_delay: int = 30):
        """
        Run agent
        :param max_retries: the maximum number of retries before giving up
        :param base_delay: the initial delay between retries, in seconds
        @return:
        """
        logger.info('Starting Agent')

        attempt = 0

        while True:
            attempt += 1
            try:
                self._construct_chain().handle(self.request)
                return
            except NoSuchWindowException:
                logger.warning('Selenium window was closed...')
                return
            except (WscmWebdriverRetryFailedException, WebDriverException, WsmcWebDriverLoginError) as e:

                self.request.driver.save_screenshot_safe(self._get_screenshot_prefix(attempt))
                if attempt == max_retries:
                    raise

                if attempt > 1 and self.request.was_retry_successful:
                    logger.warning('Resetting agent attempt count')
                    attempt = 1

                delay = base_delay * 2 ** (attempt - 1)

                logger.error(
                    f"Agent run attempt {attempt} failed, at '{self.request.driver.get_current_url_safe}',  retrying in {delay} seconds...",
                    exc_info=e
                )

                self.request.configure_for_retry()

                self.request.close_driver()
                time.sleep(delay)
            finally:
                self.request.close_driver()

    def _construct_chain(self) -> Collector:
        sm_type = self.request.get_social_media_type
        logger.info(f'Generating chain for {sm_type}')
        if sm_type == SocialMediaTypes.FB:
            login_handler = FbLoginCollector()
            login_handler.set_next(FbProfileCollector().set_next(FbPostsCollector()))
            return login_handler
        elif sm_type == SocialMediaTypes.VK:

            stack = []

            if self.request.has_entity(SocialMediaEntities.LOGIN):
                stack.append(VkLoginCollector())

            if self.request.has_entity(SocialMediaEntities.PROFILE):
                stack.append(VkProfileCollector())

            if self.request.has_entity(SocialMediaEntities.GROUP):
                stack.append(VkGroupCollector())

            if self.request.has_entity(SocialMediaEntities.POSTS):
                stack.append(VkPostsCollector())

            if self.request.has_entity(SocialMediaEntities.UNKNOWN_PROFILES):
                stack.append(VkSecondaryProfilesCollector())

            base = stack.pop(0)
            base.set_options(self.request.options)

            previous_element = base
            while len(stack) > 0:
                current_elem = stack.pop(0)

                current_elem.set_options(self.request.options)

                previous_element.set_next(current_elem)
                previous_element = current_elem

            return base

        elif sm_type == SocialMediaTypes.OK:
            login_handler = OkSeleniumLoginCollector()
            login_handler.set_next(OkSeleniumProfileCollector().set_next(OkSeleniumPostsCollector()))
            return login_handler
        else:
            raise RuntimeError(f'No suitable chain for social media {sm_type}')
