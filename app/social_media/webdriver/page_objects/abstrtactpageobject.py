from abc import ABC

from django.conf import settings
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class AbstractPageObject(ABC):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def get_wait(self, timeout: float = settings.WSMC_SELENIUM_WAIT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)
