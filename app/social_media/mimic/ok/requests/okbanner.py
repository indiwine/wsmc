from __future__ import annotations

import dataclasses

from dataclasses_json import dataclass_json
from django.conf import settings

from social_media.mimic.ok.device import AndroidDevice


@dataclass_json
@dataclasses.dataclass
class OkBannerItem:
    # Required

    euname: str
    asid: str
    instance_id: str
    device: str
    advertising_id: str

    # Semi optional
    bl: str = '90'
    mm_tt: str = '6228115456'
    mv_av: str = '4966748160'
    dpi: str = '420'
    sim_loc: str = '310'
    sim_operator_id: str = '310260'
    density: str = '2.625'
    h: str = '2400'
    w: str = '1080'
    osver: str = '13'
    vpw: str = '1080'
    appbuild: str = settings.MIMIC_OK_APP_BUILD
    appver: str = settings.MIMIC_OK_APP_VER
    operator_name: str = 'T-Mobile'
    operator_id: str = '260'

    # Optional
    rs: str = '1'
    timezone: str = 'GMT GMT'
    dkm: str = '0'
    bs: str = '4'
    btms: str = '23299'
    tscr: str = '1'
    advertising_tracking_enabled: str = '1'
    rooted: str = '0'
    connection: str = 'WIFI'
    app_lang: str = 'ru'
    lang: str = 'en'
    uimd: str = '1'
    app: str = 'ru.ok.android'
    os: str = 'Android'
    connection_type: str = 'WIFI'
    asis: str = '1'
    manufacture: str = 'Google'
    autosart: str = 'true'

    @staticmethod
    def build_from_device(device: AndroidDevice) -> OkBannerItem:
        """
        Build OkBannerItem from AndroidDevice
        @param device:
        @return:
        """
        return OkBannerItem(
            euname=device.codename,
            instance_id=device.instance_id,
            device=device.model,
            advertising_id=device.gaid,
            asid=device.asid,
            osver=device.os_version,
            density=device.density,
            h=device.h,
            w=device.w,
            vpw=device.w,
            dpi=device.dpi,
        )
