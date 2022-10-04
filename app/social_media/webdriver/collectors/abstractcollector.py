from __future__ import annotations

from abc import ABC, abstractmethod

from ..request import Request


class Collector(ABC):
    @abstractmethod
    def set_next(self, collector: Collector) -> Collector:
        pass

    @abstractmethod
    def handle(self, request: Request):
        pass


class AbstractCollector(Collector):
    _next_collector: Collector = None

    def set_next(self, collector: Collector) -> Collector:
        self._next_collector = collector
        return collector

    @abstractmethod
    def handle(self, request: Request):
        if self._next_collector:
            return self._next_collector.handle(request)
        return None
