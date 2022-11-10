from abc import ABC

from telegram_connection.agent import TgAgent
from telegram_connection.agent.responses.chatresponse import ChatResponse


class AbstractInteractionRequest(ABC):
    chat: ChatResponse

    def __init__(self, agent: TgAgent):
        self.agent = agent

    def set_chat(self, chat: ChatResponse):
        self.chat = chat
