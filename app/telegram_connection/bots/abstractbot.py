from abc import ABC, abstractmethod


class AbstractBot(ABC):
    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """
        Name of the bot
        Usually starts from @ symbol
        """
        pass

    @staticmethod
    @abstractmethod
    def get_code() -> str:
        """
        Bot codename must be unique to the system and shell not be changed during bot lifetime
        """
        pass

    @staticmethod
    @abstractmethod
    def get_chat_name() -> str:
        """
        Chat name of this bot (usually appears after subscribing to the bot)
        """
        pass
