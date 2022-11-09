from .abstractbot import AbstractBot


class GetFbBot(AbstractBot):
    @staticmethod
    def get_name() -> str:
        return '@getfb_bot'

    @staticmethod
    def get_code() -> str:
        return 'getfb'

    @staticmethod
    def get_chat_name() -> str:
        return 'getfb'
