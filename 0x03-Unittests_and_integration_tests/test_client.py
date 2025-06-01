#!/usr/bin/env python3
"""Unit and Integration tests for client.py"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test org method returns expected result"""
        test_payload = {"login": org_name}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, test_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch("client.GithubOrgClient.org",
           new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test _public_repos_url returns correct URL"""
        mock_org.return_value = {"repos_url": "http://example.com/org/repos"}
        client = GithubOrgClient("example")
        self.assertEqual(client._public_repos_url, "http://example.com/org/repos")

    @patch("client.get_json")
    @patch("client.GithubOrgClient._public_repos_url",
           new_callable=PropertyMock)
    def test_public_repos(self, mock_url, mock_get_json):
        """Test public_repos method returns expected repo names"""
        mock_url.return_value = "http://fake.url"
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]

        client = GithubOrgClient("test")
        result = client.public_repos()
        self.assertEqual(result, ["repo1", "repo2"])
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with("http://fake.url")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns correct boolean"""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)
