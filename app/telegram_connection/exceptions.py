class NoResponseWrapperFound(Exception):
    pass


class TgAgentErrors(Exception):
    pass


class ChatNotFound(TgAgentErrors):
    pass
