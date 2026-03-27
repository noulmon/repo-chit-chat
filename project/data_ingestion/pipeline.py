import logging

from data_ingestion.fetcher import fetch_repo_zip
from data_ingestion.parser import parse_repo_zip

logger = logging.getLogger(__name__)


def run_pipeline(repo_owner: str, repo_name: str) -> list[dict]:
    logger.info(f"Starting pipeline for {repo_owner}/{repo_name}")
    zip_bytes = fetch_repo_zip(repo_owner, repo_name)
    data = parse_repo_zip(zip_bytes)
    logger.info(f"Pipeline complete: {len(data)} documents ingested")
    return data
