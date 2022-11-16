from .basicmessagecontent import BasicMessageContent


class MessageText(BasicMessageContent):
    @property
    def get_text(self) -> str:
        return self.palin_text

    @staticmethod
    def supported_type() -> str:
        return 'messageText'

    @property
    def palin_text(self):
        return self.content['text']['text']
