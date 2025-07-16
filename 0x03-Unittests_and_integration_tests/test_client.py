#!/usr/bin/env python3
"""Test client.GithubOrgClient.org method."""

import unittest
from parameterized import parameterized
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient.org method."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('utils.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct payload."""
        # Set up the mock return value
        test_payload = {"name": org_name}
        mock_get_json.return_value = test_payload

        # Create client instance
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Assert the result matches the test payload
        self.assertEqual(result, test_payload)
        # Assert get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

