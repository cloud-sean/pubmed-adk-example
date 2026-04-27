# pubmed-adk-example

A multi-agent **PubMed / biomedical research assistant** built on
[Google ADK](https://adk.dev/) (Agent Development Kit) and **Gemini 3
Flash**, deployable to **Vertex AI Agent Engine**.

A coordinator agent delegates user questions to one of three
specialists:

| Sub-agent                  | Backend                  | Cost  |
|----------------------------|--------------------------|-------|
| `literature_search_agent`  | NCBI E-utilities         | Free  |
| `entity_analysis_agent`    | PubTator3                | Free  |
| `deep_research_agent`      | BigQuery PMC + Vertex AI | Paid (gated by `GOOGLE_CLOUD_PROJECT`) |

Twelve total tools cover keyword/author/PMID search, citation tracking,
biomedical entity annotation + relationship discovery, and semantic /
full-text search over PubMed Central.

## Quick start

```bash
git clone https://github.com/cloud-sean/pubmed-adk-example.git
cd pubmed-adk-example

python3 -m venv venv
source venv/bin/activate
pip install -r pubmed_agent/requirements.txt

gcloud auth application-default login
cp pubmed_agent/.env.example pubmed_agent/.env
# edit pubmed_agent/.env and set GOOGLE_CLOUD_PROJECT

adk web        # browser dev UI; pick `pubmed_agent` from the dropdown
```

Try: *"Find recent clinical trials and reviews on antibody-drug
conjugates for HER2-low metastatic breast cancer published between 2023
and 2025, then list the genes and drug targets most frequently mentioned
across them."*

## Full docs

See **[`pubmed_agent/README.md`](pubmed_agent/README.md)** for:

- Detailed architecture
- Optional BigQuery setup (dataset, connection, IAM, embedding model)
- Cost table for the paid tools
- Local run instructions (`adk web` / `adk run`)
- `adk deploy agent_engine` recipe for Vertex AI Agent Engine
- Test queries grouped by sub-agent
- Troubleshooting

## Repository layout

```
pubmed-adk-example/
├── README.md                     ← you are here
├── requirements.txt              ← workspace-level (just `google-adk`)
├── llms-full.txt                 ← ADK reference (for context, ~2.6MB)
└── pubmed_agent/                 ← the agent package
    ├── README.md                 ← full setup + deploy guide
    ├── agent.py                  ← root_agent (coordinator)
    ├── sub_agents/
    ├── tools/
    ├── test_agent.py             ← smoke tests + suggested LLM queries
    ├── requirements.txt
    └── .env.example
```

## Smoke test

```bash
source venv/bin/activate
python -m pubmed_agent.test_agent
```

Calls every free tool against live NCBI / PubTator3 APIs (no LLM, no
token cost). BigQuery tools auto-run if `GOOGLE_CLOUD_PROJECT` is set;
the ~$0.62 full-text test stays skipped unless `RUN_FULLTEXT=1`.
