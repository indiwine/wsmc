from .basicmessagecontent import BasicMessageContent


class MessageDocument(BasicMessageContent):
    @property
    def get_text(self) -> str:
        return self.text_caption

    @staticmethod
    def supported_type() -> str:
        return 'messageDocument'

    @property
    def text_caption(self):
        return self.content['caption']['text']
