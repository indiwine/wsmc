import dataclasses

from dataclasses_json import dataclass_json
from django.conf import settings

@dataclass_json
@dataclasses.dataclass
class AndroidDevice:
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
    gaid: str
    install_id: str
    android_id: str
    instance_id: str

    asid: str
    """
    Mistery UUID parameter
    """

    def get_user_agent(self) -> str:
        """
        Generate user agent string
        @return:
        """
        return generate_ok_ua(self)

    def get_device_id(self) -> str:
        """
        Generate device ID string
        @return:
        """
        return generate_ok_device_id(self)


default_device: AndroidDevice = AndroidDevice(
    name='Pixel 6',
    codename='oriole',
    model='Pixel 6',
    manufacturer='Google',
    build='RP1A.201005.004',
    w='1080',
    h='2400',
    dpi='420',
    density='2.625',
    gaid='274b6ed2-4358-496e-a1ae-892e52242549',
    install_id='a34865a3-021c-4f9b-aab7-6eac042e8884',
    android_id='66de9c2ac05fd4f2',
    instance_id='96d333bb-02d1-4a3b-9df8-e37a2e8a33d5',
    os_version='13',
    asid='1fcb452c-1c1d-5508-f436-ff9e8ace33b3'
)

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

def get_device() -> AndroidDevice:
    # TODO: implement device selection, return default for now
    return default_device
