#!/usr/bin/env python3
"""
Unit and Integration tests for client.py
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD  # Ensure this is defined in fixtures.py


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
            "name": f"{org_name_param} Org"  # Example name construction
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
        """Test public_repos lists repos using specific patching (Task 6)."""
        repos_payload = [
            {"name": "repo-alpha"},
            {"name": "repo-beta"},
            {"name": "repo-gamma"},
        ]
        mock_get_json.return_value = repos_payload

        # This URL is what _public_repos_url (mocked below) should return
        expected_repos_url = ("https://api.github.com/orgs/testorg/"
                              "specific_repos_url")

        # Task 6: Use patch as a context manager for _public_repos_url
        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock) as mock_public_url_prop:
            mock_public_url_prop.return_value = expected_repos_url

            client = GithubOrgClient("any_org_name_ok_here")
            list_of_repo_names = client.public_repos()

            expected_names = ["repo-alpha", "repo-beta", "repo-gamma"]
            self.assertEqual(list_of_repo_names, expected_names)

            # Assert the mocked property was accessed
            mock_public_url_prop.assert_called_once()

        # Assert get_json (mocked via decorator) was called correctly
        mock_get_json.assert_called_once_with(expected_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        (
            {"license": {"key": "mit"}, "name": "MIT Licensed Repo"},
            "MIT",  # Assuming key comparison might be case-sensitive
            False
        ),
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"name": "No Key License"}}, "mit", False),
    ])
    def test_has_license(self, repo_payload, license_key, expected_result):
        """Test the static method has_license with various inputs."""
        actual_has_license = GithubOrgClient.has_license(
            repo_payload, license_key
        )
        self.assertEqual(actual_has_license, expected_result)


# Two blank lines before a new class definition (PEP 8)
@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient, mocking external requests.
    Uses fixtures defined in TEST_PAYLOAD for parameterization.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up class method to patch requests.get before any tests run.
        This method is called once for each set of parameters in TEST_PAYLOAD.
        """
        # Define a side_effect function for the requests.get mock
        def requests_get_side_effect(url):
            mock_response = Mock()
            # Expected URL for the organization's details based on current fixtures
            expected_org_url = GithubOrgClient.ORG_URL.format(
                org=cls.org_payload["login"]
            )
            # Expected URL for the organization's repositories list
            expected_repos_url = cls.org_payload["repos_url"]

            if url == expected_org_url:
                mock_response.json.return_value = cls.org_payload
            elif url == expected_repos_url:
                mock_response.json.return_value = cls.repos_payload
            else:
                # For unexpected URLs, simulate a 404 or error
                mock_response.status_code = 404
                mock_response.json.side_effect = ValueError(
                    f"Unexpected URL: {url}"
                )
            return mock_response

        # Start the patcher for 'requests.get'.
        # Ensure 'client.requests.get' is the correct path where requests.get
        # is used by the code under test (e.g., within client.get_json).
        cls.get_patcher = patch('client.requests.get')

        mocked_get_function = cls.get_patcher.start()
        mocked_get_function.side_effect = requests_get_side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Tear down class method to stop the patcher after all tests have run.
        """
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """
        Test GithubOrgClient.public_repos in an integration context.
        This test uses class attributes (e.g., self.org_payload,
        self.expected_repos) that are set by @parameterized_class
        from the TEST_PAYLOAD fixtures.
        """
        client = GithubOrgClient(self.org_payload["login"])
        actual_repo_names = client.public_repos()
        self.assertEqual(actual_repo_names, self.expected_repos)

    # If your task requires testing with a specific license filter using
    # the apache2_repos fixture, you would add another test method here.
    # For example:
    # def test_public_repos_with_apache2_license(self):
    #     """Test public_repos with apache-2.0 license filter."""
    #     client = GithubOrgClient(self.org_payload["login"])
    #     # Assuming public_repos method can take a license argument:
    #     # actual_repos = client.public_repos(license="apache-2.0")
    #     # self.assertEqual(actual_repos, self.apache2_repos)
    # This depends on GithubOrgClient.public_repos supporting license filtering
    # and the specific requirements of your integration tests.


if __name__ == '__main__':
    unittest.main()
