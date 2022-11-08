from abc import ABC, abstractmethod

from telegram.utils import AsyncResult


class BasicResponse(ABC):

    @staticmethod
    @abstractmethod
    def define_applicable_type() -> str:
        pass

    def __init__(self, result: AsyncResult):
        # if not result.ok_received:
        #     raise RuntimeError('Cannot wrap response that are not yet received or has an error response')
        self.result = result

    @property
    def update(self) -> dict:
        return self.result.update
