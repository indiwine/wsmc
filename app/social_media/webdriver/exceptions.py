class WsmcWebdriverException(Exception):
    pass


class WsmcWebDriverLoginError(WsmcWebdriverException):
    pass


class WsmcWebDriverProfileException(WsmcWebdriverException):
    pass


class WsmcWebDriverGroupException(WsmcWebdriverException):
    pass


class WsmcWebDriverPostException(WsmcWebdriverException):
    pass


class WsmcWebDriverPostImageException(WsmcWebDriverPostException):
    pass

class WsmcWebDriverPostLikesException(WsmcWebDriverPostException):
    pass
