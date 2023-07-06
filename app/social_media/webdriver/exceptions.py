class WsmcWebdriverException(Exception):
    pass


class WscmWebdriverRetryFailedException(WsmcWebdriverException):
    pass


class WsmcWebDriverLoginError(WsmcWebdriverException):
    pass


class WsmcWebDriverProfileException(WsmcWebdriverException):
    pass


class WsmcWebDriverProfileNotFoundException(WsmcWebdriverException):
    pass


class WsmcWebDriverGroupNotFoundException(WsmcWebdriverException):
    pass


class WsmcWebDriverGroupException(WsmcWebdriverException):
    pass


class WsmcStopPostCollection(WsmcWebdriverException):
    pass


class WsmcWebDriverPostException(WsmcWebdriverException):
    pass


class WsmcWebDriverPostImageException(WsmcWebDriverPostException):
    pass


class WsmcWebDriverPostLikesException(WsmcWebDriverPostException):
    pass


class WsmcWebDriverNativeApiCallTimout(WsmcWebdriverException):
    pass
