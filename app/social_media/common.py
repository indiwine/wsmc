import logging
from dataclasses import dataclass, is_dataclass, asdict
from typing import get_origin, get_args, Union

logger = logging.getLogger(__name__)


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


def nested_dataclass(*dec_args, **dec_kwargs):
    """
    Decorator for nested dataclasses
    Supports nested dataclasses, Optional, List of dataclasses, List of Optional dataclasses

    Clears all unknown fields from kwargs and generates soft warning. This is done to avoid errors when new fields are added to dataclass.
    Takes into account all fields from parent dataclasses.


    @return:
    """

    def wrapper(cls):

        cls = dataclass(cls, **dec_kwargs)
        original_init = cls.__init__

        def __init__(_selfish_, *args, **kwargs):
            # Nested dataclasses are always initialized with kwargs
            if args:
                raise ValueError(f'Nested dataclasses are always initialized with kwargs. Got {args} for {cls}')

            # Let's check if dataclass is extended from another dataclass
            # If so, then we need to take to account all fields from parent dataclasses
            # We will use __annotations__ for this
            cls_fields = set(cls.__annotations__.keys())
            for base in cls.__bases__:
                if is_dataclass(base):
                    cls_fields.update(set(base.__annotations__.keys()))

            # Remove all unknown fields from kwargs
            unknown_fields = set(kwargs.keys()) - cls_fields
            if unknown_fields:
                logger.warning(f'Unknown fields {unknown_fields} for {cls}. They will be removed.')
                for field in unknown_fields:
                    del kwargs[field]

            # Create new objects for nested dataclasses
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
                    # Let's check if all items are dicts
                    if not all(isinstance(item, dict) for item in value):
                        logger.info(
                            f'List of dataclasses {field_type} contains non-dict items. They will be skipped. At {cls} field {name}.')
                        continue

                    cls_to_create = get_args(field_type)[0]
                    new_list = [cls_to_create(**item) for item in value]
                    kwargs[name] = new_list

            # Call original init with new kwargs
            original_init(_selfish_, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(dec_args[0]) if dec_args else wrapper


def dataclass_asdict_skip_none(obj):
    """
    Same as dataclasses.asdict, but skips None values
    @param obj:
    @return:
    """
    return asdict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if total == 0:
        return

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {iteration}/{total} {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
