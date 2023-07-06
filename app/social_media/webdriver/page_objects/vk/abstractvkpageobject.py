import logging
from typing import Tuple

from ..abstrtactpageobject import AbstractPageObject
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy

logger = logging.getLogger(__name__)


class AbstractVkPageObject(AbstractPageObject):
    NOT_FOUND_TITLE = '404 Not Found'

    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy):
        super().__init__(driver)
        self.link_strategy = link_strategy

    @staticmethod
    def parse_oid(oid: str) -> Tuple[str, bool]:
        is_group = oid[0] == '-'
        if is_group:
            oid = oid[1:]

        return oid, is_group

    def is_404(self):
        return self.driver.title == self.NOT_FOUND_TITLE
