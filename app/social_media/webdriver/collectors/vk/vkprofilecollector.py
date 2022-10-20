from ..abstractcollector import AbstractCollector
from ... import Request


class VkProfileCollector(AbstractCollector):
    def handle(self, request: Request):
        return super().handle(request)
