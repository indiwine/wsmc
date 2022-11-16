from .basicresponse import BasicResponse


class CallbackQueryAnswer(BasicResponse):
    @staticmethod
    def define_applicable_type() -> str:
        return 'callbackQueryAnswer'
