class WsmcWebdriverException(Exception):
    pass


class WsmcWebDriverLoginError(WsmcWebdriverException):
    pass


class WsmcWebDriverProfileException(WsmcWebdriverException):
    pass


class WsmcWebDriverPostException(WsmcWebdriverException):
    pass


class WsmcWebDriverPostImageException(WsmcWebDriverPostException):
    pass
