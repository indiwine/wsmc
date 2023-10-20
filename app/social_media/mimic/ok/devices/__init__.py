from typing import List

from social_media.mimic.ok.devices.androiddevice import AndroidDevice
from social_media.mimic.ok.devices.oneplusnord25g import ONEPLUS_NORD2_5G
from social_media.mimic.ok.devices.pixel6 import PIXEL_6
from social_media.mimic.ok.devices.pixel7 import PIXEL_7
from social_media.mimic.ok.devices.pocox3nfc import POCO_X3_NFC
from social_media.mimic.ok.devices.redminote12 import REDMI_NOTE_12
from social_media.mimic.ok.devices.xiaomimi11pro import XIAOMI_MI11_PRO

DEVICE_LIST: List[AndroidDevice] = [
    ONEPLUS_NORD2_5G,
    PIXEL_6,
    PIXEL_7,
    POCO_X3_NFC,
    REDMI_NOTE_12,
    XIAOMI_MI11_PRO]
