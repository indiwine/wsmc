from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import asdict, fields, Field, is_dataclass
from typing import Callable

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

    def get_or_create_sm_profile(self, request) -> SmProfile:
        try:
            sm_profile = self.get_sm_profile(request)
        except SmProfile.DoesNotExist:
            sm_profile = SmProfile(credentials=request.credentials, suspect=request.social_media_account.suspect)
        return sm_profile

    @staticmethod
    def assign_dto_to_obj(dto, model):
        """
        @param dto:
        @param model:
        """
        for key, value in asdict(dto).items():
            setattr(model, key, value)

    @classmethod
    def as_dict_fields_filter(cls, obj, condition: Callable[[Field], bool], dict_factory=dict):
        if is_dataclass(obj):
            result = []
            for f in fields(obj):
                if condition(f):
                    value = cls.as_dict_fields_filter(getattr(obj, f.name), condition, dict_factory)
                    result.append((f.name, value))
            return dict_factory(result)
        elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
            return type(obj)(*[cls.as_dict_fields_filter(v, condition, dict_factory) for v in obj])
        elif isinstance(obj, (list, tuple)):
            return type(obj)(cls.as_dict_fields_filter(v, condition, dict_factory) for v in obj)
        elif isinstance(obj, dict):
            return type(obj)((cls.as_dict_fields_filter(k, condition, dict_factory),
                              cls.as_dict_fields_filter(v, condition, dict_factory))
                             for k, v in obj.items())
        else:
            return copy.deepcopy(obj)

    @classmethod
    def as_dict_for_model(cls, obj):
        def conditional_filter(field: Field) -> bool:
            return not ('transient' in field.metadata and field.metadata['transient'])
        return cls.as_dict_fields_filter(obj, conditional_filter)

