from typing import List, Optional

from .basicreplymarkup import BasicReplyMarkup
from .buttons.inlinekeyboardbutton import InlineKeyboardButton
from .buttons.basicbutton import BasicButton


class InlineKeyboard(BasicReplyMarkup):
    @staticmethod
    def supported_type() -> str:
        return 'replyMarkupInlineKeyboard'

    rows: List[List[InlineKeyboardButton]] = []

    def __init__(self, reply_markup: dict):
        super().__init__(reply_markup)
        self._init_rows()

    def _init_rows(self):
        result = []
        for row in self.reply_markup['rows']:
            row_result = []
            for item in row:
                row_result.append(InlineKeyboardButton(item))
            result.append(row_result)
        self.rows = result

    def has_btn_with_text(self, text: str) -> bool:
        return bool(self.find_btn_by_text(text))

    def find_btn_by_text(self, text) -> Optional[BasicButton]:
        for row in self.rows:
            for item in row:
                if text in item.text:
                    return item
        return None
