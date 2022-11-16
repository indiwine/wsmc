from abc import ABC, abstractmethod


class BasicButton(ABC):
    def __init__(self, btn_data: dict):
        self.btn_data = btn_data

    @property
    @abstractmethod
    def text(self) -> str:
        pass

    @property
    @abstractmethod
    def data(self) -> str:
        pass
