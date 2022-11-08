from typing import List, Optional

from .basicresponse import BasicResponse


class ChatsResponse(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'chats'

    @property
    def total(self) -> int:
        return self.update['total_count']

    @property
    def chat_ids(self) -> List[int]:
        return self.update['chat_ids']

    @property
    def chats_count(self) -> int:
        return len(self.chat_ids)

    @property
    def first_chat_id(self) -> Optional[int]:
        total = self.chats_count
        if total == 0:
            return None

        return self.chat_ids[0]

    @property
    def last_chat_id(self) -> Optional[int]:
        ids = self.chat_ids
        total = self.chats_count
        if total == 0:
            return None

        return ids[total - 1]
