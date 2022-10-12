from abc import ABC

from django.conf import settings
from selenium.webdriver.support.wait import WebDriverWait, POLL_FREQUENCY
from seleniumwire.webdriver import Remote


class AbstractPageObject(ABC):
    def __init__(self, driver: Remote):
        self.driver = driver

    def get_wait(self, timeout: float = settings.WSMC_SELENIUM_WAIT_TIMEOUT, poll_frequency: float = POLL_FREQUENCY) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout, poll_frequency)
