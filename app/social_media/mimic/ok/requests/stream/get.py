import dataclasses
from copy import copy
from typing import Optional, Union, Type, List

from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest, GenericResponse, \
    RESPONSE_BODY, AbstractResponse, GenericResponseBody
from social_media.mimic.ok.requests.common import dataclass_asdict_skip_none, nested_dataclass
from social_media.mimic.ok.requests.okbanner import OkBannerItem


@dataclasses.dataclass
class FeedItem:
    pattern: str
    type: str
    date: str
    date_ms: int
    title_tokens: List[dict]
    message_tokens: List[dict]
    mark_as_spam_id: str
    feed_stat_info: str
    has_similar: bool
    actions: List[str]
    actor_refs: List[str]
    author_refs: List[str]
    owner_refs: List[str]
    target_refs: List[str]
    active: bool
    hot_news: bool
    discussion_summary: Optional[dict] = None
    place_refs: Optional[List[str]] = None

    @property
    def first_media_topic_id(self) -> str:
        """
        @return: first media topic id found in target_refs (NOTE: the media_topic: prefix is removed)
        """
        for target_ref in self.target_refs:
            if target_ref.startswith('media_topic:'):
                return target_ref.split(':')[-1]
        raise ValueError('No media topic id found in target_refs')


@dataclasses.dataclass
class FeedMediaTopicLikeSummary:
    count: int
    self: bool
    like_id: str
    like_possible: bool
    unlike_possible: bool
    use_default_reaction: bool
    reactions: Optional[list] = None
    last_like_date_ms: Optional[int] = None


@dataclasses.dataclass
class FeedMediaTopicReShareSummary:
    count: int
    self: bool
    self_owner: bool
    reshare_like_id: str
    reshare_possible: bool
    reshare_available_for_chats: bool
    reshare_object_ref: str
    reshare_available_for_external: Optional[bool] = None
    reshare_external_link: Optional[str] = None
    last_reshare_date_ms: Optional[int] = None


@nested_dataclass
class FeedMediaTopic:
    media: list
    id: str
    created_ms: int
    discussion_summary: dict
    like_summary: FeedMediaTopicLikeSummary
    reshare_summary: FeedMediaTopicReShareSummary
    ref: str
    author_ref: str
    owner_ref: str
    has_more: bool
    is_product: bool
    on_moderation: bool
    has_extended_stats: bool
    is_feeling: bool
    app_ref: Optional[str] = None
    capabilities: Optional[str] = None
    is_commenting_denied: Optional[bool] = None


@nested_dataclass
class FeedEntity:
    groups: list
    media_topics: List[FeedMediaTopic]
    music_albums: list
    music_artists: list
    music_playlists: list
    music_tracks: list
    promo_feed_buttons: list
    photo_ext_ts_buttons: list
    apps: Optional[list] = None
    videos: Optional[list] = None
    group_photos: Optional[list] = None
    group_albums: Optional[list] = None
    users: Optional[list] = None


class StreamGetResponseBody(GenericResponseBody):
    def __init__(self, raw_params: Union[dict, list]):
        self.feeds: List[FeedItem] = []
        self.entities: FeedEntity = None
        self.anchor: Optional[str] = None
        self.available: Optional[bool] = None
        super().__init__(raw_params)

    def find_media_topic(self, feed_item: FeedItem) -> FeedMediaTopic:
        """
        Find media topic corresponding to feed item
        @param feed_item:
        @return:
        """
        for media_topic in self.entities.media_topics:
            if media_topic.id == feed_item.first_media_topic_id:
                return media_topic
        raise ValueError('No media topic found')


class StreamGetResponse(GenericResponse[StreamGetResponseBody]):
    @staticmethod
    def get_body_class() -> Type[RESPONSE_BODY]:
        return StreamGetResponseBody

    def set_from_raw(self, raw_response: Union[dict, list]):
        response = copy(raw_response)
        response['feeds'] = self.build_feed_items(response['feeds'])
        response['entities'] = self.build_feed_entities(response['entities'])
        super().set_from_raw(response)

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

    gid: str
    app_suffix: str = 'android.1'
    banner_opt: str = None
    count: str = '20'
    direction: str = 'FORWARD'
    features: str = 'PRODUCT.1'
    fieldset: str = 'android.130'
    mark_as_read: bool = False
    patternset: str = 'android.80'
    reason: str = 'USER_REQUEST'
    seen_info: Optional[str] = None
    anchor: Optional[str] = None


class StreamGetRequest(GenericRequest[AbstractRequestParams]):
    def __init__(self, gid: str):
        params = StreamGetParams(gid)
        super().__init__('stream', 'get', params)

    @staticmethod
    def bound_response_cls() -> Type[AbstractResponse]:
        return StreamGetResponse
