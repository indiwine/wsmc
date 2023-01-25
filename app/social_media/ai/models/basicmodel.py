from abc import ABC, abstractmethod


class BasicModel(ABC):

    @abstractmethod
    def load(self):
        pass
