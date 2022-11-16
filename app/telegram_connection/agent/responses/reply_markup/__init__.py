from typing import List, Type

from .basicreplymarkup import BasicReplyMarkup
from .inlinekeyboard import InlineKeyboard

reply_markup_cls: List[Type[BasicReplyMarkup]] = [InlineKeyboard]
