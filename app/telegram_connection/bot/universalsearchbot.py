from .abstractbot import AbstractBot


class UniversalSearchBot(AbstractBot):

    @staticmethod
    def get_name() -> str:
        return 'universal_search'
