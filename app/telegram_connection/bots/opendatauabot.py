from .abstractbot import AbstractBot


class OpenDataUABot(AbstractBot):
    @staticmethod
    def get_name() -> str:
        return '@OpenDataUABot'

    @staticmethod
    def get_code() -> str:
        return 'open_data_ua_bot'

    @staticmethod
    def get_chat_name() -> str:
        return 'OpenDataUA'
