import dataclasses
import datetime
import logging
from copy import copy
from typing import Optional, Union, Type, List, Tuple, Generator

from django.utils import timezone

from social_media.dtos import AuthorDto, SmPostDto
from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, GenericResponse, \
    RESPONSE_BODY, AbstractResponse, GenericResponseBody
from social_media.common import dataclass_asdict_skip_none
from social_media.mimic.ok.requests.okbanner import OkBannerItem
from social_media.mimic.ok.requests.stream.entities.basefeedentity import BaseFeedEntity
from social_media.mimic.ok.requests.stream.entities.feedentity import FeedEntity
from social_media.mimic.ok.requests.stream.entities.feedgroup import FeedGroup
from social_media.mimic.ok.requests.stream.entities.feedgroupalbum import FeedGroupAlbum
from social_media.mimic.ok.requests.stream.entities.feedgroupphoto import FeedGroupPhoto
from social_media.mimic.ok.requests.stream.entities.feeditem import FeedItem
from social_media.mimic.ok.requests.stream.entities.feedmediatopic import FeedMediaTopic
from social_media.mimic.ok.requests.stream.entities.feeduser import FeedUser
from social_media.mimic.ok.requests.stream.entities.feedvideo import FeedVideo
from social_media.social_media import SocialMediaTypes

logger = logging.getLogger(__name__)

class StreamGetResponseBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.feeds: Optional[List[FeedItem]] = None
        self.entities: Optional[FeedEntity] = None
        self.anchor: Optional[str] = None
        self.available: Optional[bool] = None
        super().__init__(raw_params)

    def find_entity_by_ref(self, ref: str) \
        -> Union[FeedGroup, FeedVideo, FeedUser, FeedMediaTopic, FeedGroupAlbum, FeedGroupPhoto]:
        """
        Attempts to find entity by ref
        @param ref:
        @return:
        """

        entity_type = ref.split(':')[0]
        attr_name = f'{entity_type}s'

        if self.entities is None:
            raise ValueError(f'Entities are not present')

        if not hasattr(self.entities, attr_name):
            raise ValueError(f'No entity {entity_type} found')
        entities: List[BaseFeedEntity] = getattr(self.entities, attr_name)

        for entity in entities:
            if not dataclasses.is_dataclass(entity):
                raise NotImplementedError(f'Entity {entity_type} is not a dataclass')

            if entity.ref == ref:
                return entity

        raise ValueError(f'No entity {entity_type} with ref {ref} found')

    def find_author(self, feed_item: FeedItem) -> AuthorDto:
        """
        Find author of feed item
        @param feed_item:
        @return:
        """
        author_ref = feed_item.first_author_ref
        entity: Union[FeedGroup, FeedUser] = self.find_entity_by_ref(author_ref)
        return entity.to_author_dto()

    def item_to_post_dto(self, feed_item: FeedItem) -> Tuple[SmPostDto, BaseFeedEntity]:
        """
        Generate SmPostDto from feed item
        @param feed_item:
        @return:
        """
        if feed_item.is_valid() is False:
            raise ValueError('Feed item is not valid')

        author_dto = self.find_author(feed_item)
        target_entity = self.find_entity_by_ref(feed_item.first_target_ref)
        permalink = target_entity.extract_permalink()
        body = feed_item.get_message()
        post_id = target_entity.ref

        post_dto = SmPostDto(
            datetime=datetime.datetime.fromtimestamp(feed_item.date_ms / 1000, tz=timezone.get_current_timezone()),
            author=author_dto,
            sm_post_id=post_id,
            social_media=SocialMediaTypes.OK,
            body=body,
            permalink=permalink,
        )
        return post_dto, target_entity

    def post_generator(self) -> Generator[Tuple[SmPostDto, BaseFeedEntity], None, None]:
        """
        Generate posts from feed items
        @return:
        """
        for feed_item in self.feeds:
            if feed_item.is_valid() is False:
                continue

            post_dto, target_entity = self.item_to_post_dto(feed_item)
            yield post_dto, target_entity


class StreamGetResponse(GenericResponse[StreamGetResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return StreamGetResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        self.raw_body = raw_response
        response = copy(raw_response)
        response['feeds'] = self.build_feed_items(response['feeds']) if 'feeds' in response else None
        response['entities'] = self.build_feed_entities(response['entities']) if 'entities' in response else None
        if response['entities'] is None or response['feeds'] is None:
            logger.warning(f'No entities or feeds found in response, {raw_response}')
        self.create_and_set_body(response)

    @staticmethod
    def build_feed_items(feed_items: List[dict]):
        feed_items = [FeedItem(**feed) for feed in feed_items]
        return feed_items

    @staticmethod
    def build_feed_entities(feed_entities: dict):
        feed_entities = FeedEntity(**feed_entities)
        return feed_entities


@dataclasses.dataclass
class StreamGetParams(AbstractRequestParams):
    def configure_before_send(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions):
        self.banner_opt = OkBannerItem.build_from_device(device).to_json()

    def to_execute_dict(self) -> dict:
        return dataclass_asdict_skip_none(self)


    app_suffix: str = 'android.1'
    banner_opt: str = None
    count: str = '20'
    direction: str = 'FORWARD'
    features: str = 'PRODUCT.1'
    fieldset: str = 'android.130'
    mark_as_read: bool = False
    patternset: str = 'android.80'
    reason: str = 'USER_REQUEST'
    gid: Optional[str] = None
    uid: Optional[str] = None
    seen_info: Optional[str] = None
    anchor: Optional[str] = None

    def __post_init__(self):
        assert self.gid or self.uid, 'Either gid or uid must be present'


class StreamGetRequest(GenericRequest[AbstractRequestParams]):
    def __init__(self, gid: Optional[str] = None, uid: Optional[str] = None, anchor: Optional[str] = None):
        params = StreamGetParams(
            gid=gid,
            uid=uid,
            anchor=anchor)
        super().__init__('stream', 'get', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return StreamGetResponse
