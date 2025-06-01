#!/usr/bin/env python3
"""
Unit and Integration tests for client.py
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD  # From fixtures.py


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
        """Test public_repos lists repos using specific patching (Task 6)."""
        repos_payload = [
            {"name": "repo-alpha"},
            {"name": "repo-beta"},
            {"name": "repo-gamma"},
        ]
        mock_get_json.return_value = repos_payload

        expected_repos_url = ("https://api.github.com/orgs/testorg/"
                              "specific_repos_url")

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
    # Class attributes org_payload, repos_payload, etc., will be injected
    # by @parameterized_class for each test run/case from TEST_PAYLOAD.

    @classmethod
    def setUpClass(cls):
        """Set up class method to patch requests.get before any tests run."""
        def requests_get_side_effect(url):
            """Side effect function for requests.get mock."""
            mock_response = Mock()
            # Determine expected URLs based on current parameterized fixtures
            # Assumes GithubOrgClient.ORG_URL is like "https://api.github.com/orgs/{org}"
            expected_org_url = GithubOrgClient.ORG_URL.format(
                org=cls.org_payload["login"]
            )
            expected_repos_url = cls.org_payload["repos_url"]

            if url == expected_org_url:
                mock_response.json.return_value = cls.org_payload
            elif url == expected_repos_url:
                mock_response.json.return_value = cls.repos_payload
            else:
                # For unexpected URLs, configure mock to simulate an HTTP error
                mock_response.status_code = 404
                mock_response.json.side_effect = ValueError(
                    f"Unexpected URL in mock: {url}"
                )
            return mock_response

        # Create the patcher for 'requests.get' used within client.py
        # The string 'client.requests.get' must match how requests.get is
        # imported and used in the module your client code calls.
        cls.get_patcher = patch('client.requests.get')

        # Start the patcher and get the mock object
        mocked_get_function = cls.get_patcher.start()
        # Assign the side_effect function to the mock
        mocked_get_function.side_effect = requests_get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class method to stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """
        Test GithubOrgClient.public_repos in an integration context.
        This method uses class attributes (e.g., self.org_payload,
        self.expected_repos) provided by @parameterized_class.
        """
        # Instantiate GithubOrgClient with the org login from the current fixture set
        client = GithubOrgClient(self.org_payload["login"])

        # Call the public_repos method (without any license filter)
        actual_repo_names = client.public_repos()

        # Assert that the returned list of repo names matches self.expected_repos
        # from the current fixture set.
        self.assertEqual(actual_repo_names, self.expected_repos)

    # Example of how you might add a test for apache2_repos if needed:
    # def test_public_repos_with_apache2_license(self):
    #     """Test public_repos with the 'apache-2.0' license filter."""
    #     client = GithubOrgClient(self.org_payload["login"])
    #     # This assumes your GithubOrgClient.public_repos method
    #     # supports a 'license' keyword argument for filtering.
    #     # actual_licensed_repos = client.public_repos(license="apache-2.0")
    #     # self.assertEqual(actual_licensed_repos, self.apache2_repos)


# Standard way to make the test file runnable
if __name__ == '__main__':
    unittest.main()
