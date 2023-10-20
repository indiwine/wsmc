class WsmcWebdriverException(Exception):
    pass


class WscmWebdriverRetryFailedException(WsmcWebdriverException):
    pass


class WsmcWebDriverLoginError(WsmcWebdriverException):
    def __init__(self, *args, is_captcha_required):
        self.is_captcha_required = is_captcha_required
        super().__init__(*args)


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


class WsmcCeleryRetryException(Exception):
    def __init__(self, exc, countdown, max_retries):
        super().__init__('Celery retry exception')
        self.max_retries = max_retries
        self.countdown = countdown
        self.exc = exc

