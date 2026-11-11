---
name: github_search
track: bonus
kind: live_api
provider: GitHub
requires_env: []
inputs: [query, sort, max_results]
outputs: [items]
side_effect: false
---
# github_search

Searches public open-source repositories on GitHub via the GitHub REST API (`https://api.github.com/search/repositories`).
Supports sorting by `stars`, `forks`, or `updated` and returns repository metadata (`title`, `url`, `source`, `summary`, `stars`, `language`).

