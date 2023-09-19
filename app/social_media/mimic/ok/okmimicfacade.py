from social_media.mimic.ok.client import OkHttpClient


class OkMimicFacade:
    """
    Facade for OK mimic requests and general logic
    """

    def __init__(self, client: OkHttpClient):
        self.client = client
