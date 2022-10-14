from __future__ import annotations

from abc import ABC

from ..abstrtactpageobject import AbstractPageObject
from ...link_builders.fb import AbstractFbLinkStrategy


class AbstractFbPageObject(AbstractPageObject, ABC):
    navigation_strategy: AbstractFbLinkStrategy = None

    def set_navigation_strategy(self, strategy: AbstractFbLinkStrategy) -> AbstractFbPageObject:
        self.navigation_strategy = strategy
        return self
