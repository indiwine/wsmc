from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import fields, Field, is_dataclass
from typing import Callable, Tuple, Optional, Union, List, TypeVar, Generic

from django.contrib.contenttypes.models import ContentType

from ..options.baseoptions import BaseOptions
from ..request import Request
from ...dtos import SmProfileDto, SmGroupDto, AuthorDto
from ...dtos.smpostdto import SmPostDto
from ...dtos.smpostimagedto import SmPostImageDto
from ...models import SmProfile, SmPost, SmPostImage, SuspectGroup, SmGroup, SmComment, SmLikes


OPTIONS = TypeVar('OPTIONS', bound=BaseOptions)
REQUEST_DATA = TypeVar('REQUEST_DATA', bound=None)

class Collector(ABC, Generic[REQUEST_DATA]):
    @abstractmethod
    def set_next(self, collector: Collector) -> Collector:
        pass

    @abstractmethod
    def handle(self, request: Request[REQUEST_DATA]):
        pass

    @abstractmethod
    def set_options(self, options: BaseOptions):
        pass


class AbstractCollector(Collector[REQUEST_DATA], Generic[REQUEST_DATA, OPTIONS]):
    def __init__(self):
        self._next_collector: Optional[Collector] = None
        self._options: Optional[OPTIONS] = None

    def set_next(self, collector: Collector) -> Collector:
        self._next_collector = collector
        return self

    def set_options(self, options: OPTIONS):
        self._options = options

    def get_options(self) -> OPTIONS:
        return self._options

    @abstractmethod
    def handle(self, request: Request[REQUEST_DATA]):
        if self._next_collector:
            return self._next_collector.handle(request)
        return None

    def persist_post(self, post: SmPostDto, origin: Union[SmGroup, SmProfile], request: Request) -> Tuple[SmPost, bool]:
        author_item, author_created = self.persist_author(post.author, request)
        saved_post, created = SmPost.objects.update_or_create(
            sm_post_id=post.sm_post_id,
            social_media=post.social_media,
            defaults={
                **self.as_dict_for_model(post),
                'author_object': author_item,
                'origin_object': origin
            })
        post.id = saved_post.id
        # if post.images:
        #     for image in post.images:
        #         self.persist_image(image, saved_post)
        #
        # request.ee.emit('post', post)

        return saved_post, created

    def persist_like(self,
                     like_author: AuthorDto,
                     target: Union[SmPost, SmComment],
                     request: Request) -> Optional[Tuple[SmLikes, bool]]:
        if like_author.is_group:
            return None

        author, _ = self.persist_author(like_author, request)
        parent_type = ContentType.objects.get_for_model(target)
        return SmLikes.objects.get_or_create(
            owner=author,
            parent_type=parent_type,
            parent_id=target.id,
            defaults={
                'owner': author,
                'parent_type': parent_type,
                'parent_id': target.id,
            }
        )

    def batch_persist_likes(self,
                            like_authors: List[AuthorDto],
                            target: Union[SmPost, SmComment],
                            request: Request):
        authors = filter(lambda item: not item.is_group, like_authors)
        authors = self.batch_persist_profiles(list(authors), request)

        parent_type = ContentType.objects.get_for_model(target)

        existing_likes = SmLikes.objects.filter(
            owner_id__in=list(authors),
            parent_type=parent_type,
            parent_id=target.id
        )

        likes_to_create = []
        for author_id in authors:
            found_like = list(filter(lambda item: item.owner_id == author_id, existing_likes))
            if not found_like:
                likes_to_create.append(
                    SmLikes(
                        owner_id=author_id,
                        parent_type=parent_type,
                        parent_id=target.id
                    )
                )

        if likes_to_create:
            SmLikes.objects.bulk_create(likes_to_create, ignore_conflicts=True)

        return len(existing_likes), len(likes_to_create)

    def batch_persist_profiles(self, like_authors: List[AuthorDto], request: Request):
        all_oids = list(map(lambda author_dto: author_dto.oid, like_authors))
        db_profiles = SmProfile.objects.filter(oid__in=all_oids, social_media=request.get_social_media_type)

        existing_profiles = []
        profiles_to_create = []
        for like_author in like_authors:
            found_profiles = list(filter(lambda item: item.oid == like_author.oid, db_profiles))
            if len(found_profiles) > 0:
                existing_profiles += found_profiles
            else:
                profiles_to_create.append(
                    SmProfile(
                        social_media=request.get_social_media_type,
                        credentials=request.credentials,
                        oid=like_author.oid,
                        name=like_author.name
                    )
                )
        if profiles_to_create:
            existing_profiles += SmProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
        return SmProfile.objects.filter(
            oid__in=all_oids,
            social_media=request.get_social_media_type
        ).values_list('id', flat=True)

    def count_likes(self, target: Union[SmPost, SmComment]) -> int:
        parent_type = ContentType.objects.get_for_model(target)
        return SmLikes.objects.filter(parent_type=parent_type, parent_id=target.id).count()

    def persist_group(self, group_dto: SmGroupDto, request: Request, suspect_group: Optional[SuspectGroup] = None) -> \
        Tuple[SmGroup, bool]:
        saved_group, created = SmGroup.objects.update_or_create(
            oid=group_dto.oid,
            social_media=group_dto.social_media,
            defaults={
                **self.as_dict_for_model(group_dto),
                'credentials': request.credentials,
                'suspect_group': suspect_group
            }
        )
        return saved_group, created

    def persist_image(self, image: SmPostImageDto, post: SmPost):
        saved_image, created = SmPostImage.objects.update_or_create(post=post, oid=image.oid, defaults={
            **self.as_dict_for_model(image),
            'post': post
        })
        image.id = saved_image.id
        image.created = created

    def persist_sm_profile(self, sm_profile: SmProfileDto, request: Request):
        return SmProfile.objects.update_or_create(social_media=request.get_social_media_type,
                                                  oid=sm_profile.oid,
                                                  defaults={
                                                      **self.as_dict_for_model(sm_profile),
                                                      'credentials': request.credentials,
                                                      'social_media': request.get_social_media_type,
                                                      'suspect_social_media': request.suspect_identity,
                                                      'was_collected': True
                                                  })

    def persist_author(self, author_dto: AuthorDto, request: Request) -> Tuple[Union[SmGroup, SmProfile], bool]:
        if author_dto.is_group:
            return SmGroup.objects.get_or_create(
                oid=author_dto.oid,
                social_media=request.get_social_media_type,
                defaults={
                    'oid': author_dto.oid,
                    'name': author_dto.name,
                    'permalink': author_dto.url,
                    'credentials': request.credentials,
                    'social_media': request.get_social_media_type
                }
            )

        return SmProfile.objects.get_or_create(
            oid=author_dto.oid,
            social_media=request.get_social_media_type,
            defaults={
                'credentials': request.credentials,
                'oid': author_dto.oid,
                'name': author_dto.name,
                'social_media': request.get_social_media_type,
            }
        )

    def get_request_origin(self, request: Request) -> Union[SmProfile, SmGroup]:
        if request.is_group_request:
            return SmGroup.objects.get(suspect_group=request.suspect_identity)

        return SmProfile.objects.get(suspect_social_media=request.suspect_identity)

    def get_sm_profile(self, request: Request):
        """
        **DEPRECATED**
        """
        return SmProfile.objects.get(credentials=request.credentials,
                                     suspect=request.suspect_identity.suspect)

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
