from abc import ABC, abstractmethod


class AbstractBot(ABC):

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        pass
