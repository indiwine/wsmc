from typing import List, Type

from .basicmessagecontent import BasicMessageContent
from .messagedocument import MessageDocument
from .messagetext import MessageText
from .messagephoto import MessagePhoto

content_type_cls: List[Type[BasicMessageContent]] = [
    MessageDocument,
    MessageText,
    MessagePhoto
]
