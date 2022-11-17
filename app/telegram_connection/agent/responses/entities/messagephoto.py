from .basicmessagecontent import BasicMessageContent


class MessagePhoto(BasicMessageContent):
    @staticmethod
    def supported_type() -> str:
        return 'messagePhoto'

    @property
    def get_text(self) -> str:
        return self.content['caption']['text']
