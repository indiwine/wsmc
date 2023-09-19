from social_media.webdriver.request import Request
from social_media.webdriver.collectors import AbstractCollector
from social_media.webdriver.pipe.abstractasyncpipeline import AbstractAsyncPipeline


class CollectorPipeline(AbstractAsyncPipeline[AbstractCollector, Request]):
    """
    Pipeline for collecting data
    """
    pass
