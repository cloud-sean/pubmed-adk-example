"""ADK tool wrappers around the BigQuery PMC backend (paid).

Only usable if `GOOGLE_CLOUD_PROJECT` is set and the project has the
`models.textembed` remote model + BigQuery↔Vertex AI connection
provisioned (see README).
"""

from typing import Any, Dict

from .api_client import (
    is_bigquery_available,
    search_by_author_bq,
    search_fulltext,
    search_semantic,
)


async def search_pubmed_semantic(
    query: str,
    max_results: int = 10,
    include_full_text: bool = False,
) -> Dict[str, Any]:
    """Semantic vector search over PMC Open Access via BigQuery (PAID).

    Cost: ~$0.08/query, ~$0.69 if include_full_text=True. Use for
    conceptual queries where keyword search would miss synonyms or
    paraphrased ideas.

    Args:
        query: Natural language query.
        max_results: Max articles (default 10).
        include_full_text: Include first 2000 chars of article text. 9x more expensive.
    """
    return await search_semantic(query, max_results, include_full_text)


async def search_fulltext_tool(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Full-text keyword search over PMC articles via BigQuery (PAID).

    Cost: ~$0.62/query (scans ~100GB). Use when terms must appear in the
    article body, not just title/abstract.

    Args:
        query: Keywords to search for in full text.
        max_results: Max articles (default 10).
    """
    return await search_fulltext(query, max_results)


async def search_author_pmc(author_name: str, max_results: int = 10) -> Dict[str, Any]:
    """Author search over PMC Open Access via BigQuery (PAID, ~$0.003/query).

    Args:
        author_name: Author name.
        max_results: Max articles (default 10).
    """
    return await search_by_author_bq(author_name, max_results)


__all__ = [
    "is_bigquery_available",
    "search_pubmed_semantic",
    "search_fulltext_tool",
    "search_author_pmc",
]
