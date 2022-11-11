from .abstractbot import AbstractBot


class InfoBazaBot(AbstractBot):
    @staticmethod
    def get_name() -> str:
        return '@infobazaa_bot'

    @staticmethod
    def get_code() -> str:
        return 'info_baza'

    @staticmethod
    def get_chat_name() -> str:
        return 'Info baza'
