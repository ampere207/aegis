import httpx
import logging
from typing import List

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API abstraction for repository listing and metadata."""

    BASE = "https://api.github.com"

    async def list_user_repos(self, access_token: str | None = None, q: str | None = None) -> List[dict]:
        """List repositories accessible to the authenticated user."""
        if not access_token:
            logger.warning("No access token provided; returning empty list")
            return []

        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with httpx.AsyncClient() as client:
                params = {"per_page": 100, "sort": "updated"}
                if q:
                    params["q"] = q
                
                r = await client.get(
                    f"{self.BASE}/user/repos",
                    headers=headers,
                    params=params,
                    timeout=10.0,
                )
                
                if r.status_code == 200:
                    data = r.json()
                    repos = []
                    for item in data:
                        repos.append({
                            "id": item.get("id"),
                            "owner": item.get("owner", {}).get("login"),
                            "name": item.get("name"),
                            "full_name": item.get("full_name"),
                            "html_url": item.get("html_url"),
                            "description": item.get("description"),
                            "visibility": item.get("visibility"),
                            "clone_url": item.get("clone_url"),
                        })
                    return repos
                else:
                    logger.error(f"GitHub API error: {r.status_code} {r.text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return []

    async def get_repository(self, owner: str, repo: str, access_token: str):
        """Get repository details from GitHub."""
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.BASE}/repos/{owner}/{repo}",
                    headers=headers,
                    timeout=10.0,
                )
                if r.status_code == 200:
                    return r.json()
                else:
                    logger.error(f"Failed to fetch repo: {r.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get repository: {e}")
            return None
    async def get_pull_request_diff(self, owner: str, repo: str, pr_number: int, access_token: str) -> str | None:
        """Fetch the unified diff of a pull request."""
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3.diff",
        }

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.BASE}/repos/{owner}/{repo}/pulls/{pr_number}",
                    headers=headers,
                    timeout=15.0,
                )
                if r.status_code == 200:
                    return r.text
                else:
                    logger.error(f"Failed to fetch PR diff: {r.status_code} {r.text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get PR diff: {e}")
            return None
