#!/usr/bin/env python3
"""
Unit and Integration tests for client.py
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class # Kept parameterized_class if used elsewhere
from client import GithubOrgClient # Assuming GithubOrgClient is in client.py
from fixtures import TEST_PAYLOAD # Assuming TEST_PAYLOAD is in fixtures.py


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")  # Mocks get_json used by GithubOrgClient
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct organization data."""
        expected_payload = {"login": org_name, "name": "Test Org"} # Example payload
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        # Accessing client.org should trigger the call to get_json
        result_org_data = client.org

        # Verify get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        # Verify the .org property returns the payload from get_json
        self.assertEqual(result_org_data, expected_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL from org data."""
        # Define a known payload that client.org would return
        known_org_payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}

        # Patch client.GithubOrgClient.org to return this known payload
        # new_callable=PropertyMock is used because .org is a property
        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org_property:
            mock_org_property.return_value = known_org_payload
            
            client = GithubOrgClient("testorg")
            # Accessing _public_repos_url should use the mocked org data
            result_repos_url = client._public_repos_url

            self.assertEqual(result_repos_url, known_org_payload["repos_url"])

    @patch("client.get_json")
    @patch("client.GithubOrgClient._public_repos_url",
           new_callable=PropertyMock)
    # Corrected order of mock arguments: mock_get_json first, then mock_public_repos_url
    def test_public_repos(self, mock_get_json, mock_public_repos_url):
        """Test that public_repos returns a list of repo names."""
        # Setup the mock for _public_repos_url property
        # This is the URL from which the list of repos will be fetched.
        test_repos_url = "https://api.github.com/orgs/testorg/repos"
        mock_public_repos_url.return_value = test_repos_url

        # Setup the mock for get_json
        # This is what get_json will return when called with test_repos_url.
        # It's a list of repo dictionaries.
        mocked_repos_payload = [
            {"name": "repo-alpha"},
            {"name": "repo-beta"},
            {"id": 123, "name": "repo-gamma", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = mocked_repos_payload

        client = GithubOrgClient("testorg")
        # Call public_repos, which should use the mocked _public_repos_url
        # and the mocked get_json.
        list_of_repo_names = client.public_repos()

        # Expected list of names
        expected_names = ["repo-alpha", "repo-beta", "repo-gamma"]
        self.assertEqual(list_of_repo_names, expected_names)

        # Verify that the _public_repos_url property was accessed once
        mock_public_repos_url.assert_called_once()
        # Verify that get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False), # Test case with no license
        ({}, "my_license", False), # Test case with missing license field
        ({"license": {"key": "mit"}}, "MIT", False), # Case sensitivity
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
    ])
    def test_has_license(self, repo_payload, license_key, expected_result):
        """Test the static method has_license with various inputs."""
        # GithubOrgClient.has_license is a static method
        self.assertEqual(
            GithubOrgClient.has_license(repo_payload, license_key),
            expected_result
        )


# This allows the test to be run directly using `python test_client.py`
if __name__ == '__main__':
    unittest.main()
