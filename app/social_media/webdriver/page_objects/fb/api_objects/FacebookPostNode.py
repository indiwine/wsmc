import datetime
from typing import Optional

metadata_types = ['CometFeedStoryMinimizedTimestampStrategy', 'CometFeedStoryBackdatedTimestampStrategy']
disabled_story_layouts = ['CometFeedStoryAggregatedContextLayoutStrategy']

class FacebookPostNode:
    def __init__(self, raw_node: dict):
        self.raw_node = raw_node

    found = False

    @property
    def get_story(self) -> dict:
        return self.raw_node['comet_sections']['content']['story']

    @property
    def get_metadata(self) -> dict:
        try:
            metadata: list[dict] = self.raw_node['comet_sections']['context_layout']['story']['comet_sections']['metadata']
        except KeyError:
            raise RuntimeError('Cannot find metadata in post')
        for item in metadata:
            if item['__typename'] in metadata_types:
                return item

        raise RuntimeError('Cannot find metadata in post')

    @property
    def get_id(self) -> str:
        return self.get_story['id']

    @property
    def get_message(self) -> Optional[str]:
        if self.get_story['message'] is not None:
            return self.get_story['message']['text']
        return None

    @property
    def get_permalink(self) -> str:
        return self.get_story['wwwURL']

    @property
    def get_creation_time_unix(self) -> int:
        return self.get_metadata['story']['creation_time']

    @property
    def get_creation_time_dt(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.get_creation_time_unix)

    @property
    def is_valid_story(self) -> bool:
        return self.raw_node['comet_sections']['context_layout']['__typename'] not in disabled_story_layouts