"""Deep research specialist — semantic + full-text search over PMC via BigQuery.

This agent is constructed only if BigQuery is available (i.e.
`GOOGLE_CLOUD_PROJECT` is set). When unavailable, `deep_research_agent`
is `None` and the coordinator excludes it from `sub_agents`.
"""

from google.adk.agents.llm_agent import Agent

from ..tools.bigquery_tools import (
    is_bigquery_available,
    search_author_pmc,
    search_fulltext_tool,
    search_pubmed_semantic,
)

MODEL = "gemini-3-flash-preview"


def _build_agent():
    if not is_bigquery_available():
        return None
    return Agent(
        model=MODEL,
        name="deep_research_agent",
        description=(
            "Specialist for deep PMC research: semantic vector search and "
            "full-text keyword search over the PMC Open Access subset via "
            "BigQuery. Use only when keyword search of titles/abstracts is "
            "insufficient — these queries cost money."
        ),
        instruction=(
            "You are a deep PubMed Central research specialist backed by "
            "BigQuery. Use `search_pubmed_semantic` for conceptual / "
            "natural-language queries where keyword overlap is unreliable "
            "(~$0.08/query). Use `search_fulltext_tool` only when the user "
            "needs terms that appear in the article body, not just "
            "title/abstract (~$0.62/query — warn the user before running). "
            "Use `search_author_pmc` for author lookups within the PMC "
            "subset. Always cite the cost of the call you ran."
        ),
        tools=[
            search_pubmed_semantic,
            search_fulltext_tool,
            search_author_pmc,
        ],
    )


deep_research_agent = _build_agent()
