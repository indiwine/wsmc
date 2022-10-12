from __future__ import annotations
from dataclasses import asdict

from abc import ABC, abstractmethod

from ..request import Request
from ...models import SmProfile


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
        return self

    @abstractmethod
    def handle(self, request: Request):
        if self._next_collector:
            return self._next_collector.handle(request)
        return None

    def get_sm_profile(self, request: Request):
        return SmProfile.objects.get(credentials=request.credentials,
                                     suspect=request.social_media_account.suspect)

    @staticmethod
    def assign_dto_to_obj(dto, model):
        for key, value in asdict(dto).items():
            setattr(model, key, value)
