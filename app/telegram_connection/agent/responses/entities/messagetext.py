class MessageText:
    def __init__(self, content: dict):
        self.content = content

    @property
    def palin_text(self):
        return self.content['text']['text']