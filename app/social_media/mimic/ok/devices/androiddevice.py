import dataclasses
from random import randrange
from typing import Optional
import uuid

from dataclasses_json import dataclass_json
from django.conf import settings


@dataclass_json
@dataclasses.dataclass(frozen=True)
class AndroidDevice:
    """
    Android device representation
    @note: although this class is called AndroidDevice, it is used for OK requests as well
    @note: although gaid, install_id, android_id, asid and instance_id are optional, they are required for actually making a request
    """

    name: str
    """
    Human readable device name
    @see https://storage.googleapis.com/play_public/supported_devices.html for full list ("marketing name" column)
    """

    codename: str
    """
    Device codename
    @see https://storage.googleapis.com/play_public/supported_devices.html for full list ("device" column)
    """

    model: str
    """
    Device model
    @see https://storage.googleapis.com/play_public/supported_devices.html for full list ("model" column)
    """

    manufacturer: str
    """
    Device manufacturer
    """

    build: str
    """
    OS build number
    """

    os_version: str
    """
    Android OS version
    """

    w: str
    h: str
    dpi: str
    density: str

    gaid: Optional[str] = None
    install_id: Optional[str] = None
    android_id: Optional[str] = None
    instance_id: Optional[str] = None
    asid: Optional[str] = None
    """
    Mistery UUID parameter
    """

    @property
    def has_all_ids(self) -> bool:
        """
        Check if device has all required IDs
        @return:
        """
        return self.gaid is not None and self.install_id is not None and self.android_id is not None and self.instance_id is not None

    def check_ids_or_raise(self):
        """
        Check if device has all required IDs and raise exception if not
        @return:
        """
        if not self.has_all_ids:
            raise ValueError('Device does not have all required IDs')

    def get_user_agent(self) -> str:
        """
        Generate user agent string
        @return:
        """
        self.check_ids_or_raise()
        return generate_ok_ua(self)

    def get_device_id(self) -> str:
        """
        Generate device ID string
        @return:
        """
        self.check_ids_or_raise()
        return generate_ok_device_id(self)

    def __str__(self):
        return f'AndroidDevice: {self.manufacturer} {self.model} ({self.codename})'


def generate_ok_ua(device: AndroidDevice) -> str:
    """
    Generate OK Android User-Agent
    @param device:
    @return:
    """
    return (f'OKAndroid/{settings.MIMIC_OK_APP_VER} b{settings.MIMIC_OK_APP_BUILD} '
            f'(Android {device.os_version}; en_US; '
            f'{device.manufacturer} {device.model} Build/{device.codename} {device.os_version} {device.build}; '
            f'{device.dpi}dpi {device.dpi}dpi {device.w}x{device.h})')


def generate_ok_device_id(device: AndroidDevice) -> str:
    """
    Generate OK device ID string
    Primarily used for auth requests
    @param device:
    @return:
    """
    return f'INSTALL_ID={device.install_id};ANDROID_ID={device.android_id};'


def generate_random_64bit_hex() -> str:
    """
    Generate random 64 bit hex string (for use as Android ID)
    @return:
    """
    return '%016x' % randrange(16 ** 16)


def copy_device_with_new_values(device: AndroidDevice, **kwargs) -> AndroidDevice:
    """
    Copy device with new values
    @param device:
    @param kwargs:
    @return:
    """
    return dataclasses.replace(device, **kwargs)


def copy_device_with_new_ids(device: AndroidDevice,
                             gaid: str,
                             install_id: str,
                             android_id: str,
                             instance_id: str,
                             asid: str
                             ) -> AndroidDevice:
    """
    Copy device with new IDs

    Just a syntactic sugar for copy_device_with_new_values
    @param asid:
    @param device:
    @param gaid:
    @param install_id:
    @param android_id:
    @param instance_id:
    @return:
    """
    return copy_device_with_new_values(device,
                                       gaid=gaid,
                                       install_id=install_id,
                                       android_id=android_id,
                                       instance_id=instance_id,
                                       asid=asid)


def copy_device_with_random_ids(device: AndroidDevice) -> AndroidDevice:
    """
    Copy device with random IDs
    @param device:
    @return:
    """
    return copy_device_with_new_ids(device,
                                    gaid=str(uuid.uuid4()),
                                    install_id=str(uuid.uuid4()),
                                    android_id=generate_random_64bit_hex(),
                                    instance_id=str(uuid.uuid4()),
                                    asid=str(uuid.uuid4())
                                    )
