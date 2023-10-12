import logging
from abc import abstractmethod
from typing import Optional, Tuple

from social_media.models import OkPostStat

from social_media.webdriver.request import Request
from social_media.webdriver.request_data.okrequestdata import OkRequestData

logger = logging.getLogger(__name__)

class OkMainLoopMixin:
    """
    Mixin for the OK collectors

    Provides main loop functionality as well as anchor management
    """
    __request: Request[OkRequestData]

    async def main_loop(self, request: Request[OkRequestData]):
        """
        Main loop of the collector

        Must be called from handle method of the collector before everything else
        @return:
        """
        self.__request = request

        # Initialize collector pipeline
        was_previous_anchor_jump = False
        current_anchor = None

        previous_session_anchor, previous_session_offset = await self.try_find_anchor_from_db()

        loop_count = 0
        while True:
            loop_count += 1
            logger.debug(f'Loop {loop_count}')

            returned_anchor, can_continue = await self.fetch_data(request, current_anchor)

            if not returned_anchor:
                logger.info('Empty anchor, stopping')
                return

            if not can_continue:
                logger.info('No more data available or empty anchor, stopping')
                return

            current_anchor = returned_anchor

            if not was_previous_anchor_jump and previous_session_anchor:
                logger.info('No new data, jumping to previous session anchor')
                current_anchor = previous_session_anchor
                was_previous_anchor_jump = True

            await self.write_anchor_to_db(current_anchor, loop_count)

    @abstractmethod
    async def fetch_data(self, request: Request[OkRequestData], previous_anchor: Optional[str]) -> Tuple[
        str | None, bool]:
        """
        Fetch data from OK
        Implement this method in the collector
        @return: anchor (next anchor or Null if no more data available which forces the loop to break),
        can_continue (True if we can continue, False to break the loop)
        """
        pass

    @abstractmethod
    async def can_jump_to_previous_anchor(self) -> bool:
        """
        Can we jump to previous anchor in case of no more new items?
        Implement this method in the collector if you wish to use this functionality
        @return: True if we can jump, False otherwise
        """
        pass

    async def write_anchor_to_db(self, current_anchor: str | None, offset: int):
        """
        Write anchor to DB

        Write occurs only if anchor is not None and offset is greater than offset in DB
        @param current_anchor:
        @param offset:
        @return:
        """
        if current_anchor:
            _, offset_in_db = await self.try_find_anchor_from_db()

            if offset_in_db is None or offset > offset_in_db:
                logger.debug(f'Writing anchor {current_anchor} to DB')

                await OkPostStat.objects.aupdate_or_create(
                    **self.get_post_stat_kwargs(),
                    defaults={
                        'last_offset': offset,
                        'last_anchor': current_anchor,
                    }
                )

    async def try_find_anchor_from_db(self) -> Tuple[str | None, int | None]:
        """
        Try to find anchor from DB
        @return: anchor, offset
        """
        try:
            post_stat = await OkPostStat.objects.aget(**self.get_post_stat_kwargs())
            return post_stat.last_anchor, post_stat.last_offset
        except OkPostStat.DoesNotExist:
            return None, None

    def get_post_stat_kwargs(self):
        """
        Get kwargs for ok post stat model to find it in DB
        @return:
        """

        identity = self.__request.suspect_identity

        if self.__request.is_group_request:
            key = 'suspect_group'
        elif self.__request.is_account_request:
            key = 'suspect_social_media'
        elif self.__request.is_place_request:
            key = 'suspect_place'
        else:
            raise RuntimeError('Unknown request type')
        return {key: identity}
