from typing import Type, List

from .basicresponse import BasicResponse
from .chatresponse import ChatResponse
from .chatsresponse import ChatsResponse
from .messageresponse import MessageResponse
from .userresponse import UserResponse

available_responses: List[Type[BasicResponse]] = [
    ChatResponse,
    ChatsResponse,
    MessageResponse,
    UserResponse
]
