from dataclasses import dataclass, is_dataclass, asdict
from typing import get_origin, get_args


def dataclass_asdict_skip_none(obj):
    """
    Same as dataclasses.asdict, but skips None values
    @param obj:
    @return:
    """
    return asdict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})


def nested_dataclass(*args, **kwargs):
    """
    Decorator for nested dataclasses

    However, modified to support `List` annotation
    @see Shamelessly stolen from https://stackoverflow.com/a/51565863
    @param args:
    @param kwargs:
    @return:
    """

    def wrapper(cls):

        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)

                # If field is dataclass and value is dict, then create new object
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj

                # If filed is List of dataclasses and value is list, then create new list of objects
                elif get_origin(field_type) == list and is_dataclass(get_args(field_type)[0]) and isinstance(value,
                                                                                                             list):

                    new_list = []
                    for item in value:
                        new_obj = get_args(field_type)[0](**item)
                        new_list.append(new_obj)

                    kwargs[name] = new_list

            # Call original init with new kwargs
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper
