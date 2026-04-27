"""Root coordinator agent for the PubMed research multi-agent system.

The coordinator delegates user queries to one of three specialist
sub-agents (literature search, deep research, entity analysis) using
ADK's automatic LLM-driven sub-agent transfer.
"""

from google.adk.agents.llm_agent import Agent

from .sub_agents import (
    deep_research_agent,
    entity_analysis_agent,
    literature_search_agent,
)

MODEL = "gemini-3-flash-preview"

_sub_agents = [literature_search_agent, entity_analysis_agent]
if deep_research_agent is not None:
    _sub_agents.append(deep_research_agent)

_bq_note = (
    "The `deep_research_agent` (BigQuery semantic / full-text search) IS "
    "available — use it for conceptual queries that require PMC full text."
    if deep_research_agent is not None
    else "The `deep_research_agent` is NOT available in this deployment "
    "(GOOGLE_CLOUD_PROJECT not configured). If a user asks for semantic or "
    "full-text PMC search, explain it is unavailable and offer "
    "literature_search_agent as a keyword-based alternative."
)

root_agent = Agent(
    model=MODEL,
    name="pubmed_coordinator",
    description=(
        "Coordinator for PubMed / biomedical literature research. Delegates "
        "to specialist sub-agents for keyword search, deep semantic "
        "research, and entity/relationship analysis."
    ),
    instruction=(
        "You are the coordinator of a PubMed research team. Route every "
        "user request to the most appropriate specialist sub-agent and let "
        "them do the work — do not call tools directly.\n\n"
        "Routing rules:\n"
        "- Keyword/author/PMID lookup, citation tracking, advanced filters "
        "(date / journal / MeSH / publication type) → `literature_search_agent`.\n"
        "- Conceptual / natural-language queries that need semantic "
        "matching, or queries that must search the body of articles → "
        "`deep_research_agent` (paid BigQuery; warn the user about cost).\n"
        "- Listing biomedical entities (genes, diseases, chemicals, "
        "species, mutations) in articles, or exploring relationships "
        "between entities (e.g. drugs that treat a disease) → "
        "`entity_analysis_agent`.\n\n"
        f"{_bq_note}\n\n"
        "If a request spans multiple specialists (e.g. find papers on X "
        "then list the genes mentioned), break it into sequential "
        "delegations. Always present the final answer with citations "
        "(title, authors, year, PMID, link)."
    ),
    sub_agents=_sub_agents,
)
