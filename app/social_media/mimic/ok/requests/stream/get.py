import dataclasses

from social_media.mimic.ok.requests.abstractrequest import AbstractRequestParams

@dataclasses.dataclass
class StreamGetParams(AbstractRequestParams):
    def to_execute_dict(self) -> dict:
        return dataclasses.asdict(self)

    gid: str
    app_suffix: str = 'android.1'
    banner_opt: dict = {"rs": "1", "mm_av": "4966748160", "euname": "sdk_gphone_x86_64", "operator_id": "260",
                        "timezone": "GMT GMT", "dkm": "0", "appver": "23.7.10", "bl": "90", "mm_tt": "6228115456",
                        "bs": "4",
                        "btms": "23299", "tscr": "1", "advertising_tracking_enabled": "1", "rooted": "0",
                        "connection": "WIFI", "app_lang": "ru", "lang": "en", "dpi": "420", "uimd": "1",
                        "sim_loc": "310",
                        "asid": "1fcb452c-1c1d-5508-f436-ff9e8ace33b3", "app": "ru.ok.android",
                        "sim_operator_id": "310260",
                        "os": "Android", "density": "2.625", "connection_type": "WIFI", "h": "2400",
                        "advertising_id": "274b6ed2-4358-496e-a1ae-892e52242549", "appbuild": "23071000", "osver": "13",
                        "vph": "2201", "asis": "1", "manufacture": "Google", "operator_name": "T-Mobile",
                        "instance_id": "96d333bb-02d1-4a3b-9df8-e37a2e8a33d5", "w": "1080", "vpw": "1080",
                        "device": "emu64xa", "autostart": "true"}
    count: str = '20'
    direction: str = 'FORWARD'
    features: str = 'PRODUCT.1'
    fieldset: str = 'android.130'
    mark_as_read: bool = False
    patternset: str = 'android.80'
    reason: str = 'USER_REQUEST'
    seen_info = {"list": [{
                              "feed_stat_info": "03000000000064df5e32001a070083000103ffffffff0000ffff00000000000000016500800000000f06016dfffffffc00000089811af8ab64df5e32"},
                          {
                              "feed_stat_info": "03000000000164df5e32001a070083000103ffffffff0000ffff0000000000000001e100800000000f0601d7ffffffff00000089811af8ab64df5e32"},
                          {
                              "feed_stat_info": "03000000000264def0a1001c07020200010301ffffff0000ffff0000000000000003021214000900001701000101000000855458ff55000101000000855458ff5522080100000089811af8ab0001a12a0000000000180cc54c6c3be20000601304d0045564df5e32"}]}
