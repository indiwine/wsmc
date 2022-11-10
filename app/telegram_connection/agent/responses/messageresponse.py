from telegram.utils import AsyncResult

from .basicresponse import BasicResponse
from .entities.messagetext import MessageText


class MessageResponse(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'message'

    def __init__(self, result: AsyncResult):
        super().__init__(result)
        self.message_text = MessageText(self.update['content'])

    @property
    def chat_id(self) -> int:
        return self.update['chat_id']

    @property
    def is_outgoing(self) -> int:
        return self.update['is_outgoing']
