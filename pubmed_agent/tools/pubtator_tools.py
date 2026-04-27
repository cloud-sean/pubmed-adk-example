"""ADK tool wrappers around PubTator3 (free biomedical entity annotation)."""

from typing import Any, Dict, List, Optional

from .api_client import (
    export_publications,
    find_entity_id,
    find_related_entities,
)


async def annotate_articles(pmids: List[str], full_text: bool = False) -> Dict[str, Any]:
    """Get biomedical entity annotations (genes, diseases, chemicals, species,
    mutations, cell lines) for one or more PubMed articles via PubTator3 (FREE).

    Args:
        pmids: List of PubMed IDs, e.g. ["32133824", "34170578"].
        full_text: If True, annotate full text where available.
    """
    return await export_publications(pmids, format="biocjson", full_text=full_text)


async def lookup_entity_id(
    query: str,
    concept: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Resolve free text to a PubTator3 entity ID (FREE).

    Converts e.g. "metformin" → "@CHEMICAL_Metformin" so it can be used
    with `find_related_entities_tool`.

    Args:
        query: Free text, e.g. "metformin", "diabetes", "BRCA1".
        concept: Optional filter — "gene", "disease", "chemical", "species", "mutation".
        limit: Max IDs to return (default 5).
    """
    return await find_entity_id(query, concept, limit)


async def find_related_entities_tool(
    entity_id: str,
    relation_type: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Find entities related to a given entity via PubTator3 relationships (FREE).

    Args:
        entity_id: Entity ID from `lookup_entity_id` (must start with "@",
            e.g. "@CHEMICAL_Metformin", "@DISEASE_Diabetes Mellitus").
        relation_type: Optional — "treat", "cause", "interact", "associate",
            "prevent", "inhibit", "stimulate".
        target_type: Optional — "gene", "disease", "chemical", "variant".
        limit: Max relations (default 10).
    """
    return await find_related_entities(entity_id, relation_type, target_type, limit)
