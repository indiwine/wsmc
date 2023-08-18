from wsmc import settings


def append_gaid_and_device_id(params: dict):
    params['deviceId'] = settings.MIMIC_OK_DEVICE_ID
    params['gaid'] = settings.MIMIC_OK_GAID
    return params
