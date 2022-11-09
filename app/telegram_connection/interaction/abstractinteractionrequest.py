from abc import ABC


class AbstractInteractionRequest(ABC):
    from telegram_connection.agent import TgAgent
    from telegram_connection.agent.responses.chatresponse import ChatResponse
    
    def __init__(self, agent: TgAgent, chat: ChatResponse):
        self.agent = agent
        self.chat = chat
