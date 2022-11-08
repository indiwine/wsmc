from .abstractbot import AbstractBot


class GetFbBot(AbstractBot):
    @staticmethod
    def get_name() -> str:
        return 'getfb'
