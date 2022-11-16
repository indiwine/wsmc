from abc import ABC, abstractmethod


class BasicMessageContent(ABC):
    @staticmethod
    @abstractmethod
    def supported_type() -> str:
        pass

    def __init__(self, content: dict):
        self.content = content

    @property
    @abstractmethod
    def get_text(self) -> str:
        pass
