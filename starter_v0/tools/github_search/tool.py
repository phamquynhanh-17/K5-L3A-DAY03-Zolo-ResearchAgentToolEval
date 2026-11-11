from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err

ALLOWED_SORTS = {"stars", "forks", "updated"}


def github_search(query: str = "", sort: str = "stars", max_results: int = 5) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if sort not in ALLOWED_SORTS:
            raise ValueError(f"sort must be one of {sorted(ALLOWED_SORTS)}, got {sort!r}")
        limit = int(max_results) if max_results is not None else 5
        if limit <= 0 or limit > 50:
            raise ValueError("max_results must be between 1 and 50")

        headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query.strip(), "sort": sort, "per_page": limit},
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        raw_items = data.get("items") or []
        items = [
            {
                "title": item.get("full_name") or item.get("name") or "",
                "url": item.get("html_url") or "",
                "source": "github.com",
                "summary": (item.get("description") or "").strip(),
                "stars": item.get("stargazers_count", 0),
                "language": item.get("language"),
            }
            for item in raw_items[:limit]
            if item.get("html_url")
        ]
        return {
            "tool": "github_search",
            "query": query.strip(),
            "sort": sort,
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)

