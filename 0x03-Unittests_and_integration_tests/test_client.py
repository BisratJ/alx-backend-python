#!/usr/bin/env python3
"""
Unit tests for client.py
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name_param, mock_get_json):
        """Test GithubOrgClient.org returns correct organization data."""
        expected_payload = {
            "login": org_name_param,
            "name": f"{org_name_param} Org"
        }
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name_param)
        result_org_data = client.org

        expected_url = f"https://api.github.com/orgs/{org_name_param}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result_org_data, expected_payload)

    def test_public_repos_url(self):
        """Test _public_repos_url returns URL from org data."""
        known_org_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org_property:
            mock_org_property.return_value = known_org_payload

            client = GithubOrgClient("testorg")
            result_repos_url = client._public_repos_url

            self.assertEqual(result_repos_url,
                             known_org_payload["repos_url"])
            mock_org_property.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos lists repos using specific patching."""
        repos_payload = [
            {"name": "repo-alpha"},
            {"name": "repo-beta"},
            {"name": "repo-gamma"},
        ]
        mock_get_json.return_value = repos_payload

        expected_repos_url = ("https://api.github.com/orgs/testorg/"
                              "repos_url_from_prop")

        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock) as mock_public_url_prop:
            mock_public_url_prop.return_value = expected_repos_url

            client = GithubOrgClient("any_org_name")
            list_of_repo_names = client.public_repos()

            expected_names = ["repo-alpha", "repo-beta", "repo-gamma"]
            self.assertEqual(list_of_repo_names, expected_names)

            mock_public_url_prop.assert_called_once()

        mock_get_json.assert_called_once_with(expected_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        (
            {"license": {"key": "mit"}, "name": "MIT Licensed Repo"},
            "MIT",
            False  # Assuming key comparison is case-sensitive
        ),
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"name": "No Key License"}}, "mit", False),
    ])
    def test_has_license(self, repo_payload, license_key, expected_result):
        """Test the static method has_license with various inputs."""
        # Line 101 fix: Assign result to a variable first to keep lines short
        # and avoid issues with inline comments on the call line.
        actual_has_license = GithubOrgClient.has_license(
            repo_payload, license_key
        )
        self.assertEqual(actual_has_license, expected_result)


if __name__ == '__main__':
    unittest.main()
