from ..abstrtactpageobject import AbstractPageObject
from ...link_builders.vk.strategies.abstractvklinkstrategy import AbstractVkLinkStrategy


class AbstractVkPageObject(AbstractPageObject):
    def __init__(self, driver, link_strategy: AbstractVkLinkStrategy):
        super().__init__(driver)
        self.link_strategy = link_strategy
