from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import fields, Field, is_dataclass
from typing import Callable, Tuple

from ..request import Request
from ...dtos import SmProfileDto
from ...dtos.smpostdto import SmPostDto
from ...dtos.smpostimagedto import SmPostImageDto
from ...models import SmProfile, SmPost, SmPostImage


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

    def persist_post(self, post: SmPostDto, sm_profile: SmProfile, request: Request) -> Tuple[SmPost, bool]:
        saved_post, created = SmPost.objects.update_or_create(sm_post_id=post.sm_post_id,
                                                              profile=sm_profile,
                                                              social_media=post.social_media,
                                                              defaults={
                                                                  **self.as_dict_for_model(post),
                                                                  'profile': sm_profile,
                                                                  'suspect': request.social_media_account.suspect
                                                              })
        post.id = saved_post.id
        if post.images:
            for image in post.images:
                self.persist_image(image, saved_post)

        request.ee.emit('post', post)

        return saved_post, created

    def persist_image(self, image: SmPostImageDto, post: SmPost):
        saved_image, created = SmPostImage.objects.update_or_create(post=post, oid=image.oid, defaults={
            **self.as_dict_for_model(image),
            'post': post
        })
        image.id = saved_image.id
        image.created = created

    def persist_sm_profile(self, sm_profile: SmProfileDto, request: Request):
        return SmProfile.objects.update_or_create(credentials=request.credentials,
                                                  suspect=request.social_media_account.suspect,
                                                  defaults={
                                                      **self.as_dict_for_model(sm_profile),
                                                      'credentials': request.credentials,
                                                      'suspect': request.social_media_account.suspect
                                                  })

    def get_sm_profile(self, request: Request):
        return SmProfile.objects.get(credentials=request.credentials,
                                     suspect=request.social_media_account.suspect)

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
