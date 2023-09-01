import dataclasses
from typing import List, Optional


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


    def get_message(self) -> str:
        """
        @return: message from message_tokens
        """
        return '\n'.join(token['text'] for token in self.message_tokens)

    @property
    def first_target_ref(self) -> str:
        """
        @return: first target ref found in target_refs
        """
        for target_ref in self.target_refs:
            return target_ref
        raise ValueError('No target ref found in target_refs')

    @property
    def first_author_ref(self):
        """
        @return: first author ref found in author_refs
        """
        for author_ref in self.author_refs:
            return author_ref
        raise ValueError('No author ref found in author_refs')
