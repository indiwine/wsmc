from .abstractbot import AbstractBot


class QuickOsintBot(AbstractBot):
    @staticmethod
    def get_name() -> str:
        return '@Qu1ck_os11nt_bot'

    @staticmethod
    def get_code() -> str:
        return 'quick_osint'

    @staticmethod
    def get_chat_name() -> str:
        return 'Quick OSINT'
