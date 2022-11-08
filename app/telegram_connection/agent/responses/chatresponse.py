from .basicresponse import BasicResponse


class ChatResponse(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'chat'

    @property
    def id(self) -> int:
        return self.update['id']

    @property
    def title(self) -> str:
        return self.update['title']
