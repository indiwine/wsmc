from typing import Union, List

def recursive_dict_search(data: Union[List, dict], key_to_search: str):
    """
    Recursively search a key in a given data
    Designed to work with a garbage JSON data to find necessary stuff
    """
    if isinstance(data, list):
        for list_item in data:
            for f_val in recursive_dict_search(list_item, key_to_search):
                yield f_val
    elif isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_search:
                yield value
            elif isinstance(value, dict) or isinstance(value, list):
                for f_val in recursive_dict_search(value, key_to_search):
                    yield f_val

