#!/usr/bin/env python3
"""
Unit and Integration tests for client.py
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
        # Line 23: Was E501, ensure payload definition is concise
        # or org_name_param is not excessively long in test cases.
        # Assuming 'Org' suffix is short enough.
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
        # Line 36: Was E501, ensure docstring line is short
        known_org_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        # Line 41: Was W293, ensure this blank line (if it existed) is empty

        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org_property:
            mock_org_property.return_value = known_org_payload

            client = GithubOrgClient("testorg")
            result_repos_url = client._public_repos_url
            # Line 50: Was E261 & E501, remove/shorten inline comments
            self.assertEqual(result_repos_url,
                             known_org_payload["repos_url"])
        # Line 52: Was W293, ensure this blank line (if it existed) is empty

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos lists repos with specific patching."""
        repos_payload = [
            {"name": "repo-alpha"},
            {"name": "repo-beta"},
            {"name": "repo-gamma"},
        ]
        # Line 62: Was E501, ensure no long inline comments
        mock_get_json.return_value = repos_payload

        # Line 66: Was E501, break long strings if necessary
        expected_repos_url = ("https://api.github.com/orgs/testorg/"
                              "repos_url_from_prop")
        # Line 67: Was W293, ensure this blank line (if it existed) is empty

        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock) as mock_public_url_prop:
            mock_public_url_prop.return_value = expected_repos_url

            client = GithubOrgClient("any_org_name")
            # Line 72: Was E261 & E501, remove/shorten inline comments
            list_of_repo_names = client.public_repos()
        # Line 73: Was W293, ensure this blank line (if it existed) is empty

            expected_names = ["repo-alpha", "repo-beta", "repo-gamma"]
            # Line 76: Was E501, ensure no long inline comments
            self.assertEqual(list_of_repo_names, expected_names)

            mock_public_url_prop.assert_called_once()

        # Line 83: Was E501, ensure no long inline comments
        mock_get_json.assert_called_once_with(expected_repos_url)

    @parameterized.expand([
        # Lines 90, 91: Were E501. Ensure tuples/dicts are not too wide.
        # Break them if necessary, or shorten string literals.
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        # Example of breaking a long parameterized line:
        (
            {"license": {"key": "mit"}, "name": "Really Long Repo Name For MIT"},
            "MIT",  # Target license key
            False   # Expected result (due to case for key)
        ),
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"name": "MIT License"}}, "mit", False),
    ])
    # Line 95: Was E303, ensure one blank line before method definition
    def test_has_license(self, repo_payload, license_key, expected_result):
        """Test the static method has_license with various inputs."""
        # Line 100: Was W291, ensure no trailing whitespace
        self.assertEqual(
            GithubOrgClient.has_license(repo_payload, license_key),
            expected_result
        )  # Line 102: Was W291, ensure no trailing whitespace


if __name__ == '__main__':
    unittest.main()
