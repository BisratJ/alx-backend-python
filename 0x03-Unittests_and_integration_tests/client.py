#!/usr/bin/env python3
"""Client module"""

from typing import Dict, List
from utils import get_json


class GithubOrgClient:
    """GithubOrgClient class"""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Constructor"""
        self.org_name = org_name

    @property
    def org(self) -> Dict:
        """Get organization information"""
        return get_json(self.ORG_URL.format(org=self.org_name))

    @property
    def _public_repos_url(self) -> str:
        """Get public repositories URL"""
        return self.org["repos_url"]

    def public_repos(self, license: str = None) -> List[str]:
        """Get list of public repos optionally filtered by license"""
        repos = get_json(self._public_repos_url)
        names = [repo["name"] for repo in repos]
        if license is None:
            return names
        return [
            repo["name"]
            for repo in repos
            if repo.get("license", {}).get("key") == license
        ]

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check if repo has specific license"""
        return repo.get("license", {}).get("key") == license_key
