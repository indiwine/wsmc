from typing import Optional

from telegram.utils import AsyncResult

from .basicresponse import BasicResponse
from .entities.messagetext import MessageText


class MessageResponse(BasicResponse):
    message_text: Optional[MessageText] = None

    @staticmethod
    def define_applicable_type() -> str:
        return 'message'

    def __init__(self, result: AsyncResult):
        super().__init__(result)
        if self.update['content']['@type'] == 'messageText':
            self.message_text = MessageText(self.update['content'])

    @property
    def chat_id(self) -> int:
        return self.update['chat_id']

    @property
    def is_outgoing(self) -> int:
        return self.update['is_outgoing']

    @property
    def has_message_text(self) -> bool:
        return self.message_text is not None
