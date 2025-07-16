#!/usr/bin/env python3
"""Test client.GithubOrgClient.org method."""

import unittest
from parameterized import parameterized
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient.org method."""

    @parameterized.expand([
        ("google", {"name": "google"}),
        ("abc", {"name": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the correct payload."""
        # Set up the mock return value
        mock_get_json.return_value = expected_payload

        # Create client instance
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Assert the result matches the expected payload
        self.assertEqual(result, expected_payload)
        # Assert get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct value."""
        # Define test payload with a known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test_org/repos"
        }

        # Patch the 'org' property to return test_payload
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value=test_payload
        ) as mock_org:
            # Create client instance
            client = GithubOrgClient("google")

            # Access the property
            result = client._public_repos_url

            # Assert the result matches the expected URL
            self.assertEqual(result, test_payload["repos_url"])

            # Ensure the org property was accessed (since it's a property)
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repo names."""
        # Define test data
        test_url = "https://api.github.com/orgs/test_org/repos"
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]        
        # Configure mocks
        mock_get_json.return_value = test_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=test_url
        ) as mock_public_repos_url:
            # Create client instance
            client = GithubOrgClient("google")
            # Call the method
            repos = client.public_repos()            
            # Assert the result matches expected repo names
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])
            # Assert mocks were called correctly
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the correct boolean value."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)
