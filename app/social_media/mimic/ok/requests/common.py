import json


def to_json_slim(obj):
    """
    Convert with a small separators
    @param obj:
    @return:
    """
    return json.dumps(obj, separators=(',', ':'))
