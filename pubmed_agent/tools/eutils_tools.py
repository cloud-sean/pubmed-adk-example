"""ADK tool wrappers around NCBI E-utilities (free PubMed API).

These are exposed to LlmAgents as plain async callables; ADK auto-wraps
them as FunctionTools using the function name + docstring + signature.
"""

from typing import Any, Dict, List, Optional

from .api_client import (
    get_article_by_pmid,
    get_article_links,
    get_citing_articles,
    search_advanced,
    search_by_author_eutils,
    search_eutils,
)


async def search_pubmed(
    query: str,
    max_results: int = 10,
    sort: str = "relevance",
) -> Dict[str, Any]:
    """Search PubMed for scientific articles via NCBI E-utilities (FREE).

    Use for most keyword/phrase searches. Supports PubMed query syntax.

    Args:
        query: PubMed search query.
            Examples: "diabetes AND GLP-1 agonists", "CRISPR[Title]",
            "cancer immunotherapy AND 2020:2024[PDAT]"
        max_results: Max articles to return (1-100, default 10).
        sort: "relevance" or "date".

    Returns:
        Dict with `articles` list and metadata (title, authors, abstract, PMID, link).
    """
    return await search_eutils(query, max_results, sort)


async def search_by_author(author_name: str, max_results: int = 10) -> Dict[str, Any]:
    """Search PubMed for articles by a specific author (FREE).

    Args:
        author_name: e.g. "Smith J", "Doudna J".
        max_results: Max articles (1-100, default 10).
    """
    return await search_by_author_eutils(author_name, max_results)


async def get_article(pmid: str) -> Dict[str, Any]:
    """Fetch a single PubMed article by PMID (FREE).

    Args:
        pmid: PubMed ID, e.g. "28375731".
    """
    return await get_article_by_pmid(pmid)


async def advanced_search(
    query: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    publication_types: Optional[List[str]] = None,
    mesh_terms: Optional[List[str]] = None,
    journal: Optional[str] = None,
    title_only: bool = False,
    max_results: int = 10,
    sort: str = "relevance",
) -> Dict[str, Any]:
    """Advanced PubMed search with date / pub-type / MeSH / journal filters (FREE).

    Args:
        query: Base query (optional if other filters supplied).
        date_from: "YYYY" or "YYYY/MM/DD".
        date_to: "YYYY" or "YYYY/MM/DD".
        publication_types: e.g. ["review", "randomized controlled trial"].
        mesh_terms: e.g. ["Diabetes Mellitus", "Metformin"].
        journal: Journal name or abbreviation.
        title_only: If True, search only the title.
        max_results: 1-100, default 10.
        sort: "relevance" or "date".
    """
    return await search_advanced(
        query=query,
        date_from=date_from,
        date_to=date_to,
        publication_types=publication_types,
        mesh_terms=mesh_terms,
        journal=journal,
        title_only=title_only,
        max_results=max_results,
        sort=sort,
    )


async def get_citing_articles_tool(pmid: str, max_results: int = 20) -> Dict[str, Any]:
    """Find articles that cite a given PubMed article (FREE forward citation search).

    Args:
        pmid: PubMed ID to find citations of.
        max_results: Max citing articles (default 20).
    """
    return await get_citing_articles(pmid, max_results)


async def get_article_links_tool(pmid: str, target_db: str = "all") -> Dict[str, Any]:
    """Get links from a PubMed article to other NCBI databases (FREE).

    Args:
        pmid: PubMed ID.
        target_db: "all", "pmc", "gene", "protein", "nucleotide", "structure", "taxonomy".
    """
    return await get_article_links(pmid, target_db)
