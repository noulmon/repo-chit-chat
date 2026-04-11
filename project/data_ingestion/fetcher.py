import logging

import requests

logger = logging.getLogger(__name__)


def fetch_repo_zip(repo_owner: str, repo_name: str, branch: str = "main") -> bytes:
    url = f"https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/{branch}"
    logger.info(f"Fetching repository zip from {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    logger.info(f"Fetched {len(resp.content)} bytes for {repo_owner}/{repo_name}")
    return resp.content
