from dataclasses import asdict


def dataclass_asdict_skip_none(obj):
    """
    Same as dataclasses.asdict, but skips None values
    @param obj:
    @return:
    """
    return asdict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})


