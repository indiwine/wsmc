from telegram_connection.models import TelegramAccount


class NoResponseWrapperFound(Exception):
    pass


class TgAgentErrors(Exception):
    pass


class ChatNotFound(TgAgentErrors):
    pass


class AccountNotLoggedIn(TgAgentErrors):
    def __init__(self, account: TelegramAccount):
        self.tg_account = account
        super().__init__(f'Login into {self.tg_account.__str__()} was not performed ')

