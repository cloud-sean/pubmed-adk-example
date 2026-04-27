#!/usr/bin/env python3
"""Smoke tests for the pubmed_agent tools and wiring.

Two layers:

1. **Tool-layer tests** — call the underlying async tool functions
   directly (no LLM, no token cost). Confirms tools talk to the live
   APIs and return well-formed dicts.

2. **Suggested LLM queries** — printed at the end. Paste these into
   `adk web` or `adk run pubmed_agent` to exercise coordinator routing
   and sub-agent delegation end-to-end.

Run from the repo root:

    source venv/bin/activate
    python -m pubmed_agent.test_agent

Set GOOGLE_CLOUD_PROJECT to additionally exercise BigQuery tools
(costs ~$0.003 + ~$0.08 per run; full-text test is skipped by default
because it costs ~$0.62).
"""

import asyncio
import os
import sys
from typing import Any, Awaitable, Callable

from .agent import root_agent
from .tools.bigquery_tools import (
    is_bigquery_available,
    search_author_pmc,
    search_pubmed_semantic,
)
from .tools.eutils_tools import (
    advanced_search,
    get_article,
    get_citing_articles_tool,
    search_by_author,
    search_pubmed,
)
from .tools.pubtator_tools import (
    annotate_articles,
    find_related_entities_tool,
    lookup_entity_id,
)


def _check(name: str, ok: bool, detail: str = "") -> bool:
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {name}{(' — ' + detail) if detail else ''}")
    return ok


async def _run(label: str, coro: Awaitable[Any], assertion: Callable[[Any], bool]) -> bool:
    try:
        result = await coro
        ok = assertion(result)
        detail = "" if ok else f"unexpected shape: {str(result)[:120]}"
        return _check(label, ok, detail)
    except Exception as e:
        return _check(label, False, f"raised {type(e).__name__}: {e}")


async def test_wiring() -> int:
    print("\n== Wiring ==")
    fails = 0
    fails += not _check("root_agent name", root_agent.name == "pubmed_coordinator")
    expected_subs = {"literature_search_agent", "entity_analysis_agent"}
    if is_bigquery_available():
        expected_subs.add("deep_research_agent")
    actual = {s.name for s in root_agent.sub_agents}
    fails += not _check(
        f"sub_agents == {sorted(expected_subs)}",
        actual == expected_subs,
        f"got {sorted(actual)}",
    )
    return fails


async def test_eutils() -> int:
    print("\n== E-utilities (free) ==")
    fails = 0
    fails += not await _run(
        "search_pubmed('CRISPR Cas9')",
        search_pubmed("CRISPR Cas9", max_results=3),
        lambda r: r.get("articles") and len(r["articles"]) > 0,
    )
    fails += not await _run(
        "search_by_author('Doudna J')",
        search_by_author("Doudna J", max_results=3),
        lambda r: r.get("articles") and len(r["articles"]) > 0,
    )
    fails += not await _run(
        "get_article('28375731')",
        get_article("28375731"),
        lambda r: r.get("article") and r["article"].get("pmid") == "28375731",
    )
    fails += not await _run(
        "advanced_search(diabetes 2023)",
        advanced_search(query="diabetes", date_from="2023", date_to="2024", max_results=3),
        lambda r: r.get("articles") is not None,
    )
    fails += not await _run(
        "get_citing_articles_tool('28375731')",
        get_citing_articles_tool("28375731", max_results=3),
        lambda r: "citing_articles" in r,
    )
    return fails


async def test_pubtator() -> int:
    print("\n== PubTator3 (free) ==")
    fails = 0
    fails += not await _run(
        "annotate_articles(['28375731'])",
        annotate_articles(["28375731"]),
        lambda r: r.get("documents") is not None,
    )
    fails += not await _run(
        "lookup_entity_id('metformin')",
        lookup_entity_id("metformin", concept="chemical", limit=3),
        lambda r: "results" in r or "error" in r,
    )
    fails += not await _run(
        "find_related_entities_tool('@CHEMICAL_Metformin')",
        find_related_entities_tool("@CHEMICAL_Metformin", limit=3),
        lambda r: "relations" in r or "error" in r,
    )
    return fails


async def test_bigquery() -> int:
    if not is_bigquery_available():
        print("\n== BigQuery (paid) == SKIPPED (GOOGLE_CLOUD_PROJECT not set)")
        return 0
    print("\n== BigQuery (paid) ==")
    fails = 0
    fails += not await _run(
        "search_author_pmc('Doudna J')  ~$0.003",
        search_author_pmc("Doudna J", max_results=2),
        lambda r: r.get("articles") is not None and not r.get("error"),
    )
    fails += not await _run(
        "search_pubmed_semantic('CRISPR gene editing')  ~$0.08",
        search_pubmed_semantic("CRISPR gene editing", max_results=2),
        lambda r: r.get("articles") is not None and not r.get("error"),
    )
    if os.environ.get("RUN_FULLTEXT") == "1":
        from .tools.bigquery_tools import search_fulltext_tool
        fails += not await _run(
            "search_fulltext_tool('CRISPR Cas9')  ~$0.62",
            search_fulltext_tool("CRISPR Cas9", max_results=2),
            lambda r: r.get("articles") is not None and not r.get("error"),
        )
    else:
        print("  [SKIP] search_fulltext_tool (set RUN_FULLTEXT=1 to enable; ~$0.62)")
    return fails


SUGGESTED_QUERIES = [
    ("literature_search_agent",
     "Find recent papers on GLP-1 agonists for type 2 diabetes."),
    ("literature_search_agent",
     "Get the article with PMID 28375731 and summarize it."),
    ("literature_search_agent",
     "Find randomized controlled trials on metformin published between 2022 and 2024."),
    ("literature_search_agent",
     "Show me papers that cite PMID 28375731."),
    ("literature_search_agent",
     "List recent papers by Jennifer Doudna."),
    ("entity_analysis_agent",
     "What genes and diseases are mentioned in PMID 28375731?"),
    ("entity_analysis_agent",
     "What chemicals are known to treat diabetes mellitus?"),
    ("entity_analysis_agent",
     "Find the PubTator3 entity ID for BRCA1, then list genes it interacts with."),
    ("deep_research_agent (BigQuery, ~$0.08)",
     "Semantically search PMC for machine-learning approaches to predicting drug interactions."),
    ("deep_research_agent (BigQuery, ~$0.62 — high cost)",
     "Search the full text of PMC for articles mentioning 'CRISPR Cas9 off-target effects'."),
    ("multi-step delegation",
     "Find the top 3 papers on CRISPR Cas9 from 2024, then list the genes mentioned in each."),
]


def print_suggested_queries() -> None:
    print("\n== Suggested LLM test queries ==")
    print("Paste any of these into `adk web` or `adk run pubmed_agent`:\n")
    for target, q in SUGGESTED_QUERIES:
        print(f"  • [{target}]")
        print(f"    {q}\n")


async def main() -> int:
    fails = 0
    fails += await test_wiring()
    fails += await test_eutils()
    fails += await test_pubtator()
    fails += await test_bigquery()
    print_suggested_queries()
    print(f"\n{'PASS' if fails == 0 else 'FAIL'} — {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
