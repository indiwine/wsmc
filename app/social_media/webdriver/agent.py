import logging
import time
from typing import Optional, List

import urllib3
from aiohttp import ClientConnectionError, ClientResponseError
from celery import Task
from django.db import OperationalError
from pyee import EventEmitter
from selenium.common import NoSuchWindowException, WebDriverException

from .collectors import Collector
from .collectors.collectorpipeline import CollectorPipeline
from .collectors.ok.okgroupcollector import OkGroupCollector
from .collectors.ok.okinitdatacollector import OkInitDataCollector
from .collectors.ok.oklogincollector import OkLoginCollector
from .collectors.ok.okpostscollector import OkPostsCollector
from .collectors.ok.okprofilecollector import OkProfileCollector
from .collectors.ok.okprofilediscoverycollector import OkProfileDiscoveryCollector
from .collectors.vk import VkLoginCollector, VkProfileCollector, VkPostsCollector, VkSecondaryProfilesCollector, \
    VkGroupCollector
from .exceptions import WscmWebdriverRetryFailedException, WsmcWebDriverLoginError, WsmcCeleryRetryException
from .request import Request
from ..social_media import SocialMediaTypes, SocialMediaActions

logger = logging.getLogger(__name__)


class Agent:
    RESTARTABLE_EXCEPTIONS = (
        WscmWebdriverRetryFailedException,
        WebDriverException,
        WsmcWebDriverLoginError,
        ClientConnectionError,
        ClientResponseError,
        OperationalError,
        urllib3.exceptions.ProtocolError
    )

    def __init__(self, request: Request, task: Optional[Task] = None):

        self.request = request
        self.task = task
        self.event_bus = EventEmitter()
        self.event_bus.add_listener('progress', lambda progress, total: task.update_state(state='PROGRESS', meta={'progress': progress, 'total': total}))
        logger.info(f'Agent created for {request}')

    def _get_screenshot_prefix(self, attempt: int) -> str:
        result = f'agent_error_attempt_{attempt}'
        if self.task:
            result = f'{self.task.request.id}__{result}'
        return result

    async def run(self, max_retries: int = 5, base_delay: int = 30):
        """
        Run agent
        :param max_retries: the maximum number of retries before giving up
        :param base_delay: the initial delay between retries, in seconds
        @return:
        """
        logger.info('Starting Agent')

        self.request.ee = self.event_bus
        attempt = 0

        # Let's check if we have a task assigned and if we are retrying
        if self.task and self.task.request.retries:
            logger.debug('Agent is retrying, configuring request for retry (task is present)')
            attempt = self.task.request.retries
            self.request.configure_for_retry()

        while True:
            attempt += 1
            try:
                pipeline = self.construct_pipeline()
                await pipeline.execute(self.request)
                return
            except NoSuchWindowException:
                logger.warning('Selenium window was closed...')
                return
            except self.RESTARTABLE_EXCEPTIONS as e:
                delay = base_delay * 2 ** (attempt - 1)
                logger.error(
                    f"Agent run attempt {attempt} failed, at '{self.request.driver.get_current_url_safe if self.request.has_driver else 'driver less'}',  retrying in {delay} seconds...",
                    exc_info=e
                )

                if self.request.has_driver:
                    self.request.driver.save_screenshot_safe(self._get_screenshot_prefix(attempt))

                if attempt == max_retries:
                    logger.warning(f'Agent run attempt {attempt} failed, giving up...', exc_info=e)
                    raise

                if attempt > 1 and self.request.was_retry_successful:
                    logger.warning('Resetting agent attempt count')
                    attempt = 1

                self.request.close_driver()

                # todo: fix retry
                # We are in a celery task, so we can use retry
                # if self.task:
                #     logger.debug(f'Celery task detected, configuring for retry in {delay} seconds')
                #     # Regular retry task.retry() will not work here, because we are in async code
                #     # So we have to do it manually
                #     raise WsmcCeleryRetryException(exc=e, countdown=delay, max_retries=max_retries)

                # We are not in a celery task, so we have to do it manually
                self.request.configure_for_retry()
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
            if self.request.has_action_assigned(SocialMediaActions.LOGIN):
                stack.append(VkLoginCollector())

            if self.request.has_action_assigned(SocialMediaActions.PROFILE):
                stack.append(VkProfileCollector())

            if self.request.has_action_assigned(SocialMediaActions.GROUP):
                stack.append(VkGroupCollector())

            if self.request.has_action_assigned(SocialMediaActions.POSTS):
                stack.append(VkPostsCollector())

            if self.request.has_action_assigned(SocialMediaActions.UNKNOWN_PROFILES):
                stack.append(VkSecondaryProfilesCollector())
                logger.warning('Secondary profiles are deprecated and will be removed soon')

            if self.request.has_action_assigned(SocialMediaActions.PROFILES_DISCOVERY):
                logger.error('Profiles discovery is not implemented yet for VK')

        elif sm_type == SocialMediaTypes.OK:
            stack.append(OkInitDataCollector())
            if self.request.has_action_assigned(SocialMediaActions.LOGIN):
                stack.append(OkLoginCollector())

            if self.request.has_action_assigned(SocialMediaActions.PROFILE):
                stack.append(OkProfileCollector())

            if self.request.has_action_assigned(SocialMediaActions.GROUP):
                stack.append(OkGroupCollector())

            if self.request.has_action_assigned(SocialMediaActions.POSTS):
                stack.append(OkPostsCollector())

            if self.request.has_action_assigned(SocialMediaActions.UNKNOWN_PROFILES):
                logger.error('Unknown profiles are not implemented yet for OK')

            if self.request.has_action_assigned(SocialMediaActions.PROFILES_DISCOVERY):
                stack.append(OkProfileDiscoveryCollector())
        else:
            raise RuntimeError(f'No suitable filter stack for social media {sm_type}')

        # Apply request options
        for collector in stack:
            collector.set_options(self.request.options)

        return stack
