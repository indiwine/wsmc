from abc import ABC, abstractmethod
from typing import Optional

from .buttons.basicbutton import BasicButton


class BasicReplyMarkup(ABC):
    @staticmethod
    @abstractmethod
    def supported_type() -> str:
        pass

    def __init__(self, reply_markup: dict):
        self.reply_markup = reply_markup

    @abstractmethod
    def has_btn_with_text(self, text: str) -> bool:
        pass

    @abstractmethod
    def find_btn_by_text(self, text) -> Optional[BasicButton]:
        pass
