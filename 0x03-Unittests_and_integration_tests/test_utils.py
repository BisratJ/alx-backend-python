#!/usr/bin/env python3
"""
Unit tests for utils.py utility functions.
"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected_result):
        """Test access_nested_map with various inputs."""
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map, path,
                                         expected_exception):
        """Test that access_nested_map raises appropriate KeyErrors."""
        with self.assertRaises(expected_exception):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Test cases for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json returns the expected JSON payload from a URL."""
        # Mock the requests.get call within the utils.get_json scope
        with patch("utils.requests.get") as mock_requests_get:
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_requests_get.return_value = mock_response

            # Call the function that uses requests.get
            result_payload = get_json(test_url)

            # Assert that requests.get was called once with the correct URL
            mock_requests_get.assert_called_once_with(test_url)
            # Assert that the returned payload is correct
            self.assertEqual(result_payload, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for the memoize decorator."""

    def test_memoize(self):
        """
        Test that the memoize decorator caches the result of a method,
        making it behave like a property that computes its value once.
        """

        class TestClass:
            """A test class with a method and a memoized property."""

            def a_method(self):
                """A method that returns a fixed value."""
                return 42

            @memoize
            def a_property(self):
                """
                A property that calls a_method. With @memoize, it's
                expected to compute once and cache the result.
                """
                return self.a_method()

        # Patch a_method on TestClass.
        # The 'return_value' ensures that when the mocked a_method is called,
        # it returns 42, allowing a_property to compute its initial value.
        with patch.object(
            TestClass,
            "a_method",
            return_value=42
        ) as mock_a_method:
            test_instance = TestClass()

            # Access a_property twice.
            # IMPORTANT ASSUMPTION: utils.memoize makes 'a_property'
            # behave like an attribute (accessed without parentheses)
            # after the first computation. If it raised TypeError before,
            # this should fix it.
            value1 = test_instance.a_property
            value2 = test_instance.a_property

            # Check that both accesses return the correct value.
            self.assertEqual(value1, 42)
            self.assertEqual(value2, 42)

            # Check that the underlying a_method was called only once.
            mock_a_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
