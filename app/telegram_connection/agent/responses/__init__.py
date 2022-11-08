from typing import Type, List

from .basicresponse import BasicResponse
from .chatresponse import ChatResponse
from .chatsresponse import ChatsResponse

available_responses: List[Type[BasicResponse]] = [
    ChatResponse,
    ChatsResponse
]
