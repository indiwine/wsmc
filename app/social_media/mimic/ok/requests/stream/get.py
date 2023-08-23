import dataclasses
from typing import Optional

from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams, GenericRequest
from social_media.mimic.ok.requests.okbanner import OkBannerItem


class StreamGetResponseBody:
    pass

class StreamGetResponse:
    pass

@dataclasses.dataclass
class StreamGetParams(AbstractRequestParams):
    def configure_before_send(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions):
        self.banner_opt = OkBannerItem.build_from_device(device).to_json()


    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)

    gid: str
    app_suffix: str = 'android.1'
    banner_opt: str = None
    count: str = '20'
    direction: str = 'FORWARD'
    features: str = 'PRODUCT.1'
    fieldset: str = 'android.130'
    mark_as_read: bool = False
    patternset: str = 'android.80'
    reason: str = 'USER_REQUEST'
    seen_info: Optional[str] = None
    anchor: Optional[str] = None


class StreamGetRequest(GenericRequest):
    def __init__(self, gid: str):
        params = StreamGetParams(gid)
        super().__init__('stream', 'get', params)
