"""Entity analysis specialist — biomedical entities + relationships via PubTator3."""

from google.adk.agents.llm_agent import Agent

from ..tools.pubtator_tools import (
    annotate_articles,
    find_related_entities_tool,
    lookup_entity_id,
)

MODEL = "gemini-3-flash-preview"

entity_analysis_agent = Agent(
    model=MODEL,
    name="entity_analysis_agent",
    description=(
        "Specialist for biomedical entity extraction and relationship "
        "discovery via PubTator3. Use to list genes/diseases/chemicals/"
        "species/mutations mentioned in articles, look up canonical entity "
        "IDs, or discover relationships like drugs-that-treat-X."
    ),
    instruction=(
        "You are a biomedical entity analysis specialist using PubTator3. "
        "When the user wants to know what entities appear in a paper, call "
        "`annotate_articles` with the PMIDs. To explore relationships, "
        "first call `lookup_entity_id` to resolve free text (e.g. "
        "'metformin') to a canonical PubTator3 ID (e.g. "
        "'@CHEMICAL_Metformin'), then call `find_related_entities_tool` "
        "with that ID and an optional relation/target filter. Group "
        "results by entity type when summarizing."
    ),
    tools=[
        annotate_articles,
        lookup_entity_id,
        find_related_entities_tool,
    ],
)
