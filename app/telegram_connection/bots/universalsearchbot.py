from .abstractbot import AbstractBot


class UniversalSearchBot(AbstractBot):

    @staticmethod
    def get_code() -> str:
        return 'universal_search'

    @staticmethod
    def get_chat_name() -> str:
        return 'Universal Search'

    @staticmethod
    def get_name() -> str:
        return '@UniversalSearchRobot'
