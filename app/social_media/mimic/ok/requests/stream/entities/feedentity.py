import dataclasses
from typing import List, Optional

from social_media.common import nested_dataclass
from social_media.mimic.ok.requests.stream.entities.feedgroup import FeedGroup
from social_media.mimic.ok.requests.stream.entities.feedgroupalbum import FeedGroupAlbum
from social_media.mimic.ok.requests.stream.entities.feedgroupphoto import FeedGroupPhoto
from social_media.mimic.ok.requests.stream.entities.feedmediatopic import FeedMediaTopic
from social_media.mimic.ok.requests.stream.entities.feeduser import FeedUser
from social_media.mimic.ok.requests.stream.entities.feedvideo import FeedVideo


@dataclasses.dataclass
@nested_dataclass
class FeedEntity:
    music_albums: list
    music_artists: list
    music_playlists: list
    music_tracks: list
    promo_feed_buttons: list
    photo_ext_ts_buttons: list
    groups: List[FeedGroup]
    media_topics: List[FeedMediaTopic] = None
    apps: Optional[list] = None
    videos: Optional[List[FeedVideo]] = None
    group_photos: Optional[List[FeedGroupPhoto]] = None
    group_albums: Optional[List[FeedGroupAlbum]] = None
    users: Optional[List[FeedUser]] = None
