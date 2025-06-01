#!/usr/bin/env python3
"""Utils module"""

from typing import Mapping, Any, Sequence
import requests


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access a nested object in nested_map with key path"""
    for key in path:
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Any:
    """Get JSON content from a URL"""
    response = requests.get(url)
    return response.json()


def memoize(method: Any) -> Any:
    """Memoize method results"""
    attr_name = "_{}".format(method.__name__)

    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, method(self))
        return getattr(self, attr_name)

    return property(wrapper)
