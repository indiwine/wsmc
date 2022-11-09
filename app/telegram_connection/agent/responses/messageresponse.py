from .basicresponse import BasicResponse


class MessageResponse(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'message'

    @property
    def chat_id(self) -> int:
        return self.update['chat_id']

    @property
    def is_outgoing(self) -> int:
        return self.update['is_outgoing']
