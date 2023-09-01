from social_media.mimic.ok.client import OkHttpClient
from social_media.models import SmGroup


class OkRequestData:
    """
    This is a simple class that holds necessary data between different collectors
    """

    client: OkHttpClient

    group_uid: str
    """
    Group UID
    
    Filled by OkGroupCollector
    """

    group_model: SmGroup
    """
    Group model
    Fill by OkGroupCollector
    """

