from typing import Optional

from telegram.utils import AsyncResult

from .basicresponse import BasicResponse
from .entities import content_type_cls, BasicMessageContent, MessageText
from .reply_markup import BasicReplyMarkup, reply_markup_cls


class MessageResponse(BasicResponse):
    content: Optional[BasicMessageContent] = None
    reply_markup: Optional[BasicReplyMarkup] = None

    @staticmethod
    def define_applicable_type() -> str:
        return 'message'

    def __init__(self, result: AsyncResult):
        super().__init__(result)
        self._init_msg_content()
        self._init_reply_markup()

    def _init_msg_content(self):
        content_type = self.update['content']['@type']
        for cls in content_type_cls:
            if cls.supported_type() == content_type:
                self.content = cls(self.update['content'])
                break

    def _init_reply_markup(self):
        if 'reply_markup' in self.update and self.update['reply_markup'] is not None:
            reply_markup_type = self.update['reply_markup']['@type']
            for cls in reply_markup_cls:
                if cls.supported_type() == reply_markup_type:
                    self.reply_markup = cls(self.update['reply_markup'])
                    break

    @property
    def chat_id(self) -> int:
        return self.update['chat_id']

    @property
    def id(self) -> int:
        return self.update['id']

    @property
    def is_outgoing(self) -> int:
        return self.update['is_outgoing']

    @property
    def has_message_text(self) -> bool:
        return self.content is not None

    @property
    def has_reply_markup(self) -> bool:
        return self.reply_markup is not None
