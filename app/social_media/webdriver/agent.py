import logging
import time
from typing import Optional, List

from selenium.common import NoSuchWindowException, WebDriverException

from .collectors import Collector
from .collectors.collectorpipeline import CollectorPipeline
from .collectors.ok.okgroupcollector import OkGroupCollector
from .collectors.ok.okinitdatacollector import OkInitDataCollector
from .collectors.ok.oklogincollector import OkLoginCollector
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

    async def run(self, max_retries: int = 5, base_delay: int = 30):
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
                pipeline = self.construct_pipeline()
                await pipeline.execute(self.request)
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

    def construct_pipeline(self) -> CollectorPipeline:
        pipeline = CollectorPipeline()
        pipeline.pipe(*self.construct_filter_stack())
        return pipeline

    def construct_filter_stack(self) -> List[Collector]:
        sm_type = self.request.get_social_media_type
        logger.info(f'Generating filter stack for {sm_type}')

        stack = []

        if sm_type == SocialMediaTypes.FB:
            raise NotImplementedError('FB pipeline not implemented')
        elif sm_type == SocialMediaTypes.VK:
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
        elif sm_type == SocialMediaTypes.OK:
            stack.append(OkInitDataCollector())
            if self.request.has_entity(SocialMediaEntities.LOGIN):
                stack.append(OkLoginCollector())

            if self.request.has_entity(SocialMediaEntities.GROUP):
                stack.append(OkGroupCollector())
        else:
            raise RuntimeError(f'No suitable filter stack for social media {sm_type}')

        return stack
