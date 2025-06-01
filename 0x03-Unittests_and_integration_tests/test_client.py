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
        expected_payload = {"login": org_name_param, "name": f"{org_name_param} Org"}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name_param)
        result_org_data = client.org

        expected_url = f"https://api.github.com/orgs/{org_name_param}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result_org_data, expected_payload)

    def test_public_repos_url(self):
        """Test _public_repos_url returns URL from org data."""
        # Line 37 fix: Shortened docstring
        known_org_payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}

        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org_property:
            mock_org_property.return_value = known_org_payload
            
            client = GithubOrgClient("testorg")
            result_repos_url = client._public_repos_url

            self.assertEqual(result_repos_url, known_org_payload["repos_url"])
            mock_org_property.assert_called_once()

    # Task 6: Use @patch as a decorator for get_json
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json): # Only mock_get_json is from decorator
        """Test public_repos lists repos using specific patching strategy."""
        
        # 1. Define the payload that get_json will return for the repos URL
        repos_payload = [
            {"name": "repo-alpha", "license": {"key": "mit"}},
            {"name": "repo-beta"},
            {"name": "repo-gamma"},
        ]
        mock_get_json.return_value = repos_payload

        # 2. Define the chosen value for _public_repos_url
        expected_repos_url = "https://api.github.com/orgs/testorg/repos_url_from_prop"

        # 3. Task 6: Use patch as a context manager for _public_repos_url
        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock) as mock_public_repos_url_prop:
            
            # Set the return value for the mocked _public_repos_url property
            mock_public_repos_url_prop.return_value = expected_repos_url

            # Instantiate the client
            client = GithubOrgClient("any_org_name") # Org name doesn't affect this mock
            
            # Call public_repos. This should:
            # - Access _public_repos_url (mocked to return expected_repos_url)
            # - Call get_json with expected_repos_url (mocked to return repos_payload)
            list_of_repo_names = client.public_repos()

            # Define the expected list of names from our repos_payload
            expected_names = ["repo-alpha", "repo-beta", "repo-gamma"]
            self.assertEqual(list_of_repo_names, expected_names)

            # 4. Test that the mocked property (_public_repos_url) was called once
            mock_public_repos_url_prop.assert_called_once()

        # 5. Test that mocked get_json was called once with the expected URL
        # This assertion is outside the 'with' block for the property mock,
        # as get_json is mocked for the entire method via the decorator.
        # The call to get_json happens when client.public_repos() is executed.
        # Line 62 fix: If an inline comment here was too long, it's removed or shortened.
        # For example, if this line was the culprit, ensure no long inline comment:
        mock_get_json.assert_called_once_with(expected_repos_url)


    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"license": {"key": "mit"}}, "MIT", False), 
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"name": "MIT License"}}, "mit", False), 
    ])
    def test_has_license(self, repo_payload, license_key, expected_result):
        """Test the static method has_license with various inputs."""
        self.assertEqual(
            GithubOrgClient.has_license(repo_payload, license_key),
            expected_result
        )


if __name__ == '__main__':
    unittest.main()
