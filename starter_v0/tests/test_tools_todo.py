"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is implemented offline using fake_http and monkeypatch fixtures.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
github_search_tool = TOOL_FUNCTIONS["github_search"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(
        question="Bạn muốn tìm theo nguồn nào?",
        response_type="choice",
        options=["Web", "Twitter"],
    )
    assert result["options"] == ["Web", "Twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item 2", "section": "B", "url": "https://b.com/2"},
        {"title": "Item 3", "section": "A", "url": "https://a.com/3"},
    ]
    result = format_tool(items=items, template="sections", headline="Digest")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First post", "url": "https://x.com/1"},
        {"title": "Second post", "url": "https://x.com/2"},
    ]
    result = format_tool(items=items, template="thread")
    lines = [line for line in result["markdown"].split("\n\n") if line.strip()]
    assert lines[0].startswith("1/")
    assert lines[1].startswith("2/")


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None, template="sections")
    res_empty = format_tool(items=[], template="brief")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot123:token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin AI", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", topic="general", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Hello world content",
            "metadata": {"title": "Test Page", "sourceURL": "https://example.com/article"},
        }
    }))

    result = fetch_tool(url="https://example.com/article")

    assert len(calls) == 1
    item = result["items"][0]
    assert item["title"] == "Test Page"
    assert item["url"] == "https://example.com/article"
    assert item["source"] == "example.com"
    assert item["summary"] == "Hello world content"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({
        "data": {
            "markdown": "a" * 5500,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = fetch_tool(url="https://example.com/long")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    raw_timeline = [{"text": "no id tweet", "screen_name": "sama"}] + [
        {"tweet_id": str(i), "text": f"Tweet {i}", "screen_name": "sama"}
        for i in range(1, 7)
    ]
    fake_http(FakeResponse({"timeline": raw_timeline}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"], start=1):
        assert item["url"] == f"https://x.com/sama/status/{idx}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool(query="AI agents", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "AI agents"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="   ")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="data personal privacy", policy_area="data_privacy", top_k=5)
    assert len(result["results"]) > 0
    for item in result["results"]:
        assert item["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="citation quote source", policy_area="source_citation", top_k=5)
    assert len(result["results"]) > 0
    all_untrusted = [line for r in result["results"] for line in r["untrusted_text"]]
    all_facts = " ".join(r["facts"] for r in result["results"])
    assert len(all_untrusted) > 0
    for untrusted_line in all_untrusted:
        assert untrusted_line not in all_facts


# ---------------- YOUR NEW TOOL(S): github_search ----------------

def test_my_new_tool_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "langchain-ai/langchain",
                "html_url": "https://github.com/langchain-ai/langchain",
                "description": "Build context-aware reasoning applications",
                "stargazers_count": 95000,
                "language": "Python",
            },
            {
                "full_name": "run-llama/llama_index",
                "html_url": "https://github.com/run-llama/llama_index",
                "description": "Data framework for LLM applications",
                "stargazers_count": 38000,
                "language": "Python",
            },
        ]
    }))

    result = github_search_tool(query="RAG framework", sort="stars", max_results=2)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "RAG framework", "sort": "stars", "per_page": 2}
    assert result["tool"] == "github_search"
    assert len(result["items"]) == 2
    assert result["items"][0] == {
        "title": "langchain-ai/langchain",
        "url": "https://github.com/langchain-ai/langchain",
        "source": "github.com",
        "summary": "Build context-aware reasoning applications",
        "stars": 95000,
        "language": "Python",
    }


def test_my_new_tool_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    empty_res = github_search_tool(query="   ", sort="stars")
    assert empty_res["error"] == "ValueError"
    assert "non-empty" in empty_res["message"]

    bad_sort_res = github_search_tool(query="RAG", sort="invalid_sort")
    assert bad_sort_res["error"] == "ValueError"
    assert "sort" in bad_sort_res["message"]

    bad_limit_res = github_search_tool(query="RAG", sort="stars", max_results=0)
    assert bad_limit_res["error"] == "ValueError"
    assert calls == []


def test_my_new_tool_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403, text="API rate limit exceeded"))
    result = github_search_tool(query="llm", sort="stars", max_results=5)
    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"
    assert "403" in result["message"]
