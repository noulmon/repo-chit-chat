import requests


def fetch_repo_zip(repo_owner, repo_name) -> bytes:
    prefix = "https://codeload.github.com"
    url = f"{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main"
    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    return resp.content
