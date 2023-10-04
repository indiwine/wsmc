from dataclasses import dataclass, is_dataclass, asdict
from typing import get_origin, get_args, Union


def is_optional(type_):
    """
    Checks if type is Optional
    @param type_:
    @return:
    """
    type_args = get_args(type_)
    return (
        get_origin(type_) is Union
        and len(type_args) == 2
        and type_args[1] is type(None)
    )

def unfold_optional(type_):
    """
    Unfold Optional type
    @param type_:
    @return:
    """
    type_args = get_args(type_)
    return type_args[0]

def is_list_of_dataclasses(type_):
    """
    Checks if type is List of dataclasses
    @param type_:
    @return:
    """
    type_args = get_args(type_)
    return (
        get_origin(type_) is list
        and len(type_args) == 1
        and is_dataclass(type_args[0])
    )


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

                # If field is Optional, then unfold it
                if is_optional(field_type):
                    field_type = unfold_optional(field_type)

                # If field is dataclass and value is dict, then create new object
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj

                # If filed is List of dataclasses and value is list, then create new list of objects
                elif is_list_of_dataclasses(field_type) and isinstance(value, list):

                    cls_to_create = get_args(field_type)[0]
                    new_list = [cls_to_create(**item) for item in value]
                    kwargs[name] = new_list

            # Call original init with new kwargs
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


def dataclass_asdict_skip_none(obj):
    """
    Same as dataclasses.asdict, but skips None values
    @param obj:
    @return:
    """
    return asdict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
