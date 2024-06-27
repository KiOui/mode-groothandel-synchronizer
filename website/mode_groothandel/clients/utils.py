from typing import Optional, List, Any


def get_value_or_none(data: dict, key: str, set_type=None) -> Optional[Any]:
    """
    Get a value from a dictionary or return None.

    :param data: The dictionary to get the value from.
    :param key: The key to return the value of, if the key does not exist None is returned.
    :param set_type: Whether to convert the type to something.
    :return: The value present at data[key] if the key is present, else None.
    """
    if key in data:
        value = data[key]
        if set_type is not None and value is not None:
            value = set_type(value)
        return value
    else:
        return None


def get_value_or_default(data: dict, key: str, default: Optional[Any]) -> Optional[Any]:
    """
    Get a value from a dictionary or return a default value.

    :param data: The dictionary to get the value from.
    :param key: The key to return the value of, if the key does not exist or is None the default is returned.
    :param default: The default value to return if the key does not exist in the dictionary.
    :return: The value present at data[key] if the key is present, else default.
    """
    return data[key] if key in data and data[key] is not None else default


def get_value_or_error(data: dict, key: str) -> Any:
    """
    Get a value from a dictionary or throw a KeyError if the value is not set.

    :param data: The dictionary to get the value from.
    :param key: The key to return the value of, if the key does not exist a KeyError is thrown.
    :return: The value present at data[key] if the key is present.
    """
    value = data.get(key, None)
    if value is None:
        raise KeyError("'{}' attribute should be set.".format(key))
    return value


def apply_from_data_to_list_or_error(fn_from_data, data: dict, key: str, *args, **kwargs) -> Optional[List]:
    """
    Apply a function to each element in a value present at a key or throw a KeyError if the value is not set.

    :param fn_from_data: The function to apply to the values at the key in the dictionary.
    :param data: The dictionary to retrieve the values from.
    :param key: The key of the value to retrieve from the dictionary.
    :return: The return value of fn_from_data applied to all values present at the key in the dictionary if the key
    exists.
    """
    list_obj = get_value_or_none(data, key)
    if list_obj is None:
        raise KeyError("'{}' attribute should be set.".format(key))

    return_value = list()
    for value in data[key]:
        return_value.append(fn_from_data(data=value, *args, **kwargs))

    return return_value


def apply_from_data_to_list_or_none(fn_from_data, data: dict, key: str, *args, **kwargs) -> Optional[List]:
    """
    Apply a function to each element in a value present at a key of a dictionary if that key exists, else return None.

    :param fn_from_data: The function to apply to the values at the key in the dictionary.
    :param data: The dictionary to retrieve the values from.
    :param key: The key of the value to retrieve from the dictionary.
    :return: The return value of fn_from_data applied to all values present at the key in the dictionary if the key
    exists, else None.
    """
    list_obj = get_value_or_none(data, key)
    if list_obj is None:
        return None

    return_value = list()
    for value in data[key]:
        return_value.append(fn_from_data(data=value, *args, **kwargs))

    return return_value


def apply_from_data_or_none(fn_from_data, data: dict, key: str, *args, **kwargs):
    """
    Apply a function to a value present at a key of a dictionary if that key exists, else return None.

    :param fn_from_data: The function to apply to the value at the key in the dictionary.
    :param data: The dictionary to retrieve the value from.
    :param key: The key of the value to retrieve from the dictionary.
    :return: The return value of fn_from_data applied to the value present at the key in the dictionary if the key
    exists, else None.
    """
    value = get_value_or_none(data, key)
    return fn_from_data(data=value, *args, **kwargs) if value is not None else None


def apply_from_data_or_error(fn_from_data, data: dict, key: str, *args, **kwargs):
    """
    Apply a function to a value present at a key of a dictionary if that key exists, else return a KeyError.

    :param fn_from_data: The function to apply to the value at the key in the dictionary.
    :param data: The dictionary to retrieve the value from.
    :param key: The key of the value to retrieve from the dictionary.
    :return: The return value of fn_from_data applied to the value present at the key in the dictionary if the key
    exists.
    """
    value = get_value_or_error(data, key)
    return fn_from_data(data=value, *args, **kwargs)


def apply_from_data_to_dict_or_none(fn_from_data, data: dict, key: str, *args, **kwargs) -> Optional[dict]:
    """
    Apply a function to each element in a dictionary present at a key of a dictionary if that key exists.

    None is returned if the key does not exist.

    :param fn_from_data: The function to apply to the values in the dictionary at the key in data.
    :param data: The dictionary to retrieve the values from.
    :param key: The key of the value of the dictionary to retrieve from data.
    :return: The return value of fn_from_data applied to all values of the dictionary present at the key in data if the
    key exists, else None.
    """
    dict_obj = get_value_or_none(data, key)
    if dict_obj is None:
        return None

    return_value = dict()
    for key, value in dict_obj.items():
        return_value[key] = fn_from_data(data=value, *args, **kwargs)

    return return_value


def apply_from_data_to_dict_or_error(fn_from_data, data: dict, key: str, *args, **kwargs) -> dict:
    """
    Apply a function to each element in a dictionary present at a key of a dictionary if that key exists.

    A KeyError is thrown if the key does not exist.

    :param fn_from_data: The function to apply to the values in the dictionary at the key in data.
    :param data: The dictionary to retrieve the values from.
    :param key: The key of the value of the dictionary to retrieve from data.
    :return: The return value of fn_from_data applied to all values of the dictionary present at the key in data if the
    key exists, else raise a KeyError.
    """
    dict_obj = get_value_or_none(data, key)
    if dict_obj is None:
        raise KeyError("'{}' attribute should be set.".format(key))

    return_value = dict()
    for key, value in dict_obj.items():
        return_value[key] = fn_from_data(value, *args, **kwargs)

    return return_value
