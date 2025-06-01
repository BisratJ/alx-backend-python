#!/usr/bin/env python3
"""Integration tests for GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD["org_payload"],
        "repos_payload": TEST_PAYLOAD["repos_payload"],
        "expected_repos": TEST_PAYLOAD["expected_repos"],
        "apache2_repos": TEST_PAYLOAD["apache2_repos"]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for public_repos method"""

    @classmethod
    def setUpClass(cls):
        """Set up mock patch for requests.get"""
        cls.get_patcher = patch("requests.get")

        mock_get = cls.get_patcher.start()
        mock_get.side_effect = [
            cls.org_payload,
            cls.repos_payload
        ]
        cls.mock_get = mock_get

    @classmethod
    def tearDownClass(cls):
        """Tear down the patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with Apache 2.0 license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
