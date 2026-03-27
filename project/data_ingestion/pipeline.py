from data_ingestion.fetcher import fetch_repo_zip
from data_ingestion.parser import parse_repo_zip


def run_pipeline(repo_owner, repo_name) -> list:
    zip_bytes = fetch_repo_zip(repo_owner, repo_name)
    return parse_repo_zip(zip_bytes)
