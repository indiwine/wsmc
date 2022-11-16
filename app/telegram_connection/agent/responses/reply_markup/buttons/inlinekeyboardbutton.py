from .basicbutton import BasicButton


class InlineKeyboardButton(BasicButton):

    @property
    def text(self) -> str:
        return self.btn_data['text']

    @property
    def data(self) -> str:
        return self.btn_data['type']['data']
