from abc import ABC


class BaseOptions(ABC):

    def configure_for_retry(self):
        pass
