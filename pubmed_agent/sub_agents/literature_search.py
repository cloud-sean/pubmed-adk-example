"""Literature search specialist — wraps NCBI E-utilities (free)."""

from google.adk.agents.llm_agent import Agent

from ..tools.eutils_tools import (
    advanced_search,
    get_article,
    get_article_links_tool,
    get_citing_articles_tool,
    search_by_author,
    search_pubmed,
)

MODEL = "gemini-3-flash-preview"

literature_search_agent = Agent(
    model=MODEL,
    name="literature_search_agent",
    description=(
        "Specialist for keyword/author/PMID-based PubMed searches and citation "
        "tracking using NCBI E-utilities. Use for any standard literature lookup, "
        "fetching an article by PMID, finding articles citing a paper, or "
        "filtering by date / journal / publication type / MeSH terms."
    ),
    instruction=(
        "You are a PubMed literature search specialist. Use the available NCBI "
        "E-utilities tools to find articles, fetch metadata by PMID, and trace "
        "citations. Prefer `search_pubmed` for free-form queries, "
        "`advanced_search` when the user gives explicit filters (date range, "
        "journal, MeSH terms, publication type), `search_by_author` for "
        "author-only lookups, `get_article` for a known PMID, "
        "`get_citing_articles_tool` for forward citation tracking, and "
        "`get_article_links_tool` to surface PMC full-text or related "
        "NCBI database links. Summarize results concisely with title, authors, "
        "year, PMID, and link."
    ),
    tools=[
        search_pubmed,
        search_by_author,
        get_article,
        advanced_search,
        get_citing_articles_tool,
        get_article_links_tool,
    ],
)
