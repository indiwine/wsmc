from seleniumwire.webdriver import Remote

from ..abstrtactpageobject import AbstractPageObject
from ...link_builders.ok.strategies.abstractoklinkstrategy import AbstractOkLinkStrategy


class AbstractOkPageObject(AbstractPageObject):
    def __init__(self, driver: Remote, link_strategy: AbstractOkLinkStrategy):
        super().__init__(driver)
        self.link_strategy = link_strategy
