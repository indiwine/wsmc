import dataclasses
from enum import Enum
from typing import List, Optional

from social_media.common import nested_dataclass


class FeedItemPatterns(Enum):
    CONTENT = 'CONTENT'
    PRESENT = 'PRESENT'

@nested_dataclass
class FeedItem:
    pattern: str
    type: str
    date: str
    date_ms: int
    title_tokens: List[dict]
    message_tokens: List[dict]
    feed_stat_info: str
    has_similar: bool
    author_refs: Optional[List[str]] = None
    target_refs: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    active: Optional[bool] = None
    actor_refs: Optional[List[str]] = None
    receiver_refs: Optional[List[str]] = None
    owner_refs: Optional[List[str]] = None
    present_refs: Optional[List[str]] = None
    sender_refs: Optional[List[str]] = None
    action_type: Optional[str] = None
    cover: Optional[str] = None
    group_ref: Optional[str] = None
    hot_news: Optional[bool] = None
    mark_as_spam_id: Optional[str] = None
    discussion_summary: Optional[dict] = None
    place_refs: Optional[List[str]] = None
    holiday_refs: Optional[List[str]] = None
    pinned: Optional[bool] = None
    member_status: Optional[str] = None
    


    def get_message(self) -> str:
        """
        @return: message from message_tokens
        """
        return '\n'.join(token['text'] for token in self.message_tokens)

    def is_valid(self) -> bool:
        """
        @return: True if feed item is valid
        """
        return self.pattern == FeedItemPatterns.CONTENT.value

    @property
    def first_target_ref(self) -> str:
        """
        @return: first target ref found in target_refs
        """
        if self.target_refs is not None:
            for target_ref in self.target_refs:
                return target_ref

        raise ValueError('No target ref found in target_refs')

    @property
    def first_author_ref(self):
        """
        @return: first author ref found in author_refs
        """
        if self.author_refs is not None:
            for author_ref in self.author_refs:
                return author_ref
        raise ValueError('No author ref found in author_refs')
