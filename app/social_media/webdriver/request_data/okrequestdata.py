from social_media.mimic.ok.client import OkHttpClient
from social_media.models import SmGroup, SmProfile


class OkRequestData:
    """
    This is a simple class that holds necessary data between different collectors
    """

    client: OkHttpClient = None

    group_uid: str = None
    """
    Group UID
    
    Filled by OkGroupCollector
    """

    group_model: SmGroup
    """
    Group model
    Fill by OkGroupCollector
    """

    user_id: str = None
    """
    User ID
    Filled by OkProfileCollector
    """

    profile_model: SmProfile = None
    """
    Profile model
    Filled by OkProfileCollector
    """

