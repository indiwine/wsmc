import random

from social_media.mimic.ok.devices.androiddevice import AndroidDevice, copy_device_with_new_ids, copy_device_with_random_ids

from social_media.mimic.ok.devices.pixel6 import PIXEL_6
from social_media.mimic.ok.devices import DEVICE_LIST

"""
Default device for OK,
This is a default device with the precautions taken to avoid being banned
"""
default_device = copy_device_with_new_ids(PIXEL_6,

                                          gaid='274b6ed2-4358-496e-a1ae-892e52242549',
                                          install_id='a34865a3-021c-4f9b-aab7-6eac042e8884',
                                          android_id='66de9c2ac05fd4f2',
                                          instance_id='96d333bb-02d1-4a3b-9df8-e37a2e8a33d5',
                                          asid='1fcb452c-1c1d-5508-f436-ff9e8ace33b3')


def get_random_device() -> AndroidDevice:
    """
    Pick a random device from the list of devices and generate a new device with random ids
    @return:
    """

    picked_device = random.choice(DEVICE_LIST)
    return copy_device_with_random_ids(picked_device)


