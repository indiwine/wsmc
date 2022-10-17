from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..screeningrequest import ScreeningRequest


class AbstractScreeningModule(ABC):
    _next_module: Optional[AbstractScreeningModule] = None

    def set_next(self, module: AbstractScreeningModule) -> AbstractScreeningModule:
        self._next_module = module
        return self

    @abstractmethod
    def handle(self, screening_request: ScreeningRequest):
        if self._next_module:
            return self._next_module.handle(screening_request)

        return None
