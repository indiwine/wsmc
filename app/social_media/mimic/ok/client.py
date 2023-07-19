import aiohttp

from social_media.mimic.ok.requests.abstractrequest import AbstractRequest

UA = 'OKAndroid/23.7.10 b23071000 (Android 13; en_US; Google Pixel6 Build/TQ3A.230605.010.A1; 420dpi 420dpi 1080x2201)'
APP_KEY = 'CBAFJIICABABABABA'


class OkHttpClient:
    def __init__(self):
        self._client_session = aiohttp.ClientSession(headers={
            'user-agent': UA
        })

    async def make(self, request: AbstractRequest):
        pass
