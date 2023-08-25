import dataclasses
import json
from typing import List, Optional

from django.conf import settings

from social_media.mimic.ok.okhttpclientauthoptions import OkHttpClientAuthOptions
from social_media.mimic.ok.device import AndroidDevice
from social_media.mimic.ok.log_requests.reader import OkLogStreamEncoder
from social_media.mimic.ok.requests.abstractrequest import GenericRequest, AbstractRequestParams, \
    AbstractCustomPayloadEncoderMixin


class OkLogEncoderMixin(AbstractCustomPayloadEncoderMixin):

    def encode(self, payload: dict) -> bytes:
        encoder = OkLogStreamEncoder()
        return encoder.encode(payload)

    def get_content_type(self) -> str:
        return 'application/x-www-form-urlencoded'

    def get_content_encoding(self) -> Optional[str]:
        return 'gzip'


@dataclasses.dataclass
class ExternalLogItem:
    timestamp: int
    type: int
    operation: str
    time: int
    data: list
    custom: Optional[dict] = None


@dataclasses.dataclass
class ExternalLogData:
    application: str = f'ru.ok.android:{settings.MIMIC_OK_APP_VER}:{settings.MIMIC_OK_APP_BUILD}'
    platform: str = 'unknown'
    items: List[ExternalLogItem] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ExternalLogParams(AbstractRequestParams):
    collector: str = None
    data: ExternalLogData = None

    def configure_before_send(self, device: AndroidDevice, auth_options: OkHttpClientAuthOptions):
        self.data.platform = f'android:phone:{device.os_version}'

    def to_execute_dict(self) -> dict:
        result = dataclasses.asdict(self)
        result['data'] = json.dumps(result['data'], separators=(',', ':'))
        return result


class ExternalLogRequest(GenericRequest[ExternalLogParams], OkLogEncoderMixin):
    def __init__(self, params: ExternalLogParams):
        super().__init__('log', 'externalLog', params)

    def update_timestamps_relative(self, base_timestamp: int) -> int:
        """
        Update timestamps of log items to be relative to base_timestamp
        @param base_timestamp: timestamp in milliseconds
        @return: updated timestamp set for the last log item
        """
        params: ExternalLogParams = self.params

        previous_timestamp = None
        time_to_set = None

        for log_item in params.data.items:
            # first item is always set to base_timestamp
            if previous_timestamp is None:
                time_to_set = base_timestamp
            else:
                # For the rest of the items we calculate time difference between current and previous item and add it to
                # a base timestamp
                time_to_set = abs(previous_timestamp - log_item.timestamp) + base_timestamp

            previous_timestamp = log_item.timestamp
            log_item.timestamp = time_to_set

        return time_to_set
