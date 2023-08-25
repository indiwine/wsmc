class OkApiCallException(Exception):
    def __init__(self, code: int, msg: str, data = None):
        super().__init__(msg)
        self.ok_code = code
        self.ok_data = data


class OkResponseNotFoundException(Exception):
    pass


