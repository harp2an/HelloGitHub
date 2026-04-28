#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch GitHub repository data for HelloGitHub project.

This script retrieves repository information from GitHub API,
including stars, description, language, and other metadata
used to populate HelloGitHub monthly issues.
"""

import os
import sys
import time
import logging
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 15  # seconds (increased from 10 to reduce timeout errors on slow connections)


def get_headers(token: Optional[str] = None) -> dict:
    """Build request headers, optionally including a GitHub token.

    Args:
        token: GitHub personal access token for authenticated requests.
                Unauthenticated requests are limited to 60/hour.

    Returns:
        Dictionary of HTTP headers.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_repo_info(owner: str, repo: str, token: Optional[str] = None) -> Optional[dict]:
    """Fetch metadata for a single GitHub repository.

    Args:
        owner: GitHub username or organisation name.
        repo:  Repository name.
        token: Optional GitHub personal access token.

    Returns:
        Dictionary with repository metadata, or None on failure.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    try:
        response = requests.get(url, headers=get_headers(token), timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return {
            "full_name": data.get("full_name"),
            "description": data.get("description", ""),
            "language": data.get("language", "Unknown"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "homepage": data.get("homepage", ""),
            "topics": data.get("topics", []),
            "license": (data.get("license") or {}).get("spdx_id", "N/A"),
            "html_url": data.get("html_url"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error fetching %s/%s: %s", owner, repo, exc)
    except requests.exceptions.RequestException as exc:
        logger.error("Request error fetching %s/%s: %s", owner, repo, exc)
    return None


def fetch_repos(repo_list: list[str], token: Optional[str] = None, delay: float = 1.0) -> list[dict]:
    """Fetch metadata for a list of repositories.

    Args:
        repo_list: List of "owner/repo" strings.
        token:     Optional GitHub personal access token.
   