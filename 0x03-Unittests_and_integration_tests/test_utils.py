#!/usr/bin/env python3
"""Unit tests for utils.py"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock # Assuming Mock is used if get_json is in the same file
from utils import access_nested_map, get_json, memoize


# TestAccessNestedMap class (as you provided, assuming it's correct)
class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test normal access to nested maps"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected):
        """Test exceptions raised by access_nested_map"""
        with self.assertRaises(expected):
            access_nested_map(nested_map, path)


# TestGetJson class (as you provided, assuming it's correct)
class TestGetJson(unittest.TestCase):
    """Test cases for get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json returns expected data"""
        # Ensure utils.requests.get is the correct path if utils.py uses requests directly
        with patch("utils.requests.get") as mock_get: # Or just "requests.get" if get_json imports requests directly
            mock_resp = Mock()
            mock_resp.json.return_value = test_payload
            mock_get.return_value = mock_resp

            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator"""

    def test_memoize(self):
        """Test that memoize caches method output"""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                """
                This method, when memoized, might behave like a property
                that computes its value once.
                """
                return self.a_method()

        # Pycodestyle fix: line broken for length
        with patch.object(TestClass,
                          "a_method",
                          return_value=42) as mock_method:
            test_instance = TestClass()

            # Assuming memoize makes a_property behave like a property attribute
            # Access it without parentheses
            self.assertEqual(test_instance.a_property, 42)
            self.assertEqual(test_instance.a_property, 42)
            
            mock_method.assert_called_once()

# If running this file directly (standard for unittests)
# if __name__ == '__main__':
#     unittest.main()
