from datetime import date
from time import mktime
from typing import Union, List, Callable, Any, Optional, Generator

from django.conf import settings
from icu import SimpleDateFormat, Locale


def recursive_dict_search(data: Union[List, dict],
                          key_to_search: str,
                          filter_cb: Optional[Callable[[Any], bool]] = None
                          ) -> Generator[Any, None, None]:
    """
    Recursively search a key in a given data
    Designed to work with a garbage JSON data to find necessary stuff
    """
    if isinstance(data, list):
        for list_item in data:
            for f_val in recursive_dict_search(list_item, key_to_search, filter_cb):
                yield f_val
    elif isinstance(data, dict):
        for key, value in data.items():
            value_found = False
            if key == key_to_search:
                has_filter = filter_cb is not None
                allowed_by_filter = False
                if has_filter:
                    allowed_by_filter = filter_cb(value)
                if not has_filter or (has_filter and allowed_by_filter):
                    value_found = True
                    yield value

            if not value_found and (isinstance(value, dict) or isinstance(value, list)):
                for f_val in recursive_dict_search(value, key_to_search, filter_cb):
                    yield f_val


def date_to_local_month(date_to_format: date) -> str:
    df = SimpleDateFormat('LLLL', Locale(settings.WSMC_WEBDRIVER_LOCALE))
    return df.format(mktime(date_to_format.timetuple()))
