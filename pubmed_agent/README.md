# PubMed Research Agent

A multi-agent PubMed / biomedical research assistant built on **Google ADK**
(Agent Development Kit) and **Gemini 3 Flash**, deployable to **Vertex AI
Agent Engine**.

## Architecture

```
                 ┌──────────────────────────────┐
                 │     pubmed_coordinator       │   ← root_agent
                 │  (LLM-driven sub-agent       │
                 │   transfer / delegation)     │
                 └──────────────┬───────────────┘
                                │
       ┌────────────────────────┼─────────────────────────┐
       ▼                        ▼                         ▼
┌────────────────┐    ┌──────────────────┐     ┌────────────────────┐
│ literature_    │    │ entity_analysis_ │     │ deep_research_     │
│ search_agent   │    │ agent            │     │ agent (optional)   │
│ (E-utilities)  │    │ (PubTator3)      │     │ (BigQuery PMC)     │
├────────────────┤    ├──────────────────┤     ├────────────────────┤
│ search_pubmed  │    │ annotate_articles│     │ search_pubmed_     │
│ search_by_     │    │ lookup_entity_id │     │   semantic         │
│   author       │    │ find_related_    │     │ search_fulltext_   │
│ get_article    │    │   entities       │     │   tool             │
│ advanced_      │    │                  │     │ search_author_pmc  │
│   search       │    │                  │     │                    │
│ get_citing_    │    │                  │     │                    │
│   articles     │    │                  │     │                    │
│ get_article_   │    │                  │     │                    │
│   links        │    │                  │     │                    │
└────────────────┘    └──────────────────┘     └────────────────────┘
       FREE                  FREE                       PAID
```

The `deep_research_agent` is registered only when `GOOGLE_CLOUD_PROJECT`
is set. Without it, the coordinator transparently falls back to keyword
search.

## Prerequisites

- **Python 3.11+**
- **Google Cloud SDK** (`gcloud`, `bq`) — install: <https://cloud.google.com/sdk/docs/install>
- **A GCP project with billing enabled** (used for both Vertex AI / Gemini and BigQuery)

## 1. Local setup

From the repo root (`pubmed-on-ge/`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r pubmed_agent/requirements.txt
```

## 2. Authenticate to Google Cloud

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

ADC credentials power both Vertex AI (Gemini) and BigQuery.

## 3. Configure environment

`pubmed_agent/.env` is loaded automatically by ADK. Defaults:

```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=hcls-ce-team-sandbox-736288
GOOGLE_CLOUD_LOCATION=global
```

Edit `GOOGLE_CLOUD_PROJECT` to point at your project. Optional extras:

```bash
# Optional: raises NCBI E-utilities rate limit from 3 → 10 req/sec
PUBMED_API_KEY=your_ncbi_api_key
```

If you do NOT want the BigQuery sub-agent, remove `GOOGLE_CLOUD_PROJECT`
from `.env` (Gemini still works through Vertex AI when ADC is auth'd).

## 4. (Optional) Provision BigQuery for the deep_research_agent

The semantic / full-text PMC tools require a one-time setup in your
project. **Skip this if you only need the free keyword + entity tools.**

```bash
PROJECT=YOUR_PROJECT_ID

# 4a. Enable the APIs
gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com \
    --project=$PROJECT

# 4b. Create the models dataset (US location)
bq --project_id=$PROJECT mk --location=US --dataset models

# 4c. Create a BigQuery → Vertex AI cloud-resource connection named "default"
bq --project_id=$PROJECT mk --connection \
    --location=US \
    --connection_type=CLOUD_RESOURCE default

# 4d. Grant the connection's service agent permission to call Vertex AI
SA=$(bq --project_id=$PROJECT show --location=US --connection \
    --format=json default | python3 -c \
    "import json,sys; print(json.load(sys.stdin)['cloudResource']['serviceAccountId'])")
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" \
    --role="roles/aiplatform.user"

# 4e. Wait ~60s for IAM propagation, then create the embedding model
sleep 60
bq --project_id=$PROJECT query --use_legacy_sql=false "
CREATE OR REPLACE MODEL \`$PROJECT.models.textembed\`
REMOTE WITH CONNECTION \`$PROJECT.us.default\`
OPTIONS(endpoint='text-embedding-005')
"
```

**Cost warnings** — these tools bill your project per query:

| Tool                       | Approx cost / call |
|----------------------------|--------------------|
| `search_author_pmc`        | ~$0.003            |
| `search_pubmed_semantic`   | ~$0.08             |
| `search_pubmed_semantic` + `include_full_text=True` | ~$0.69 |
| `search_fulltext_tool`     | ~$0.62             |

## 5. Run locally

From the repo root:

```bash
# Browser-based dev UI (recommended)
adk web

# Or CLI chat
adk run pubmed_agent
```

`adk web` lists `pubmed_agent` in its agent dropdown. See **Test queries**
below for things to try.

## Test queries

### Smoke test — tools only (no LLM, no token cost)

```bash
source venv/bin/activate
python -m pubmed_agent.test_agent
```

Calls every tool against live NCBI / PubTator3 / (optionally) BigQuery
APIs and reports pass/fail. BigQuery tools auto-skip unless
`GOOGLE_CLOUD_PROJECT` is set; the ~$0.62 full-text test stays skipped
unless you also set `RUN_FULLTEXT=1`. Useful as a CI-style check that
your env, ADC, and BigQuery setup all work end-to-end.

### LLM queries — paste into `adk web` or `adk run pubmed_agent`

These exercise coordinator routing into each specialist:

**`literature_search_agent` (E-utilities, free):**
- *"Find recent papers on GLP-1 agonists for type 2 diabetes."*
- *"Get the article with PMID 28375731 and summarize it."*
- *"Find randomized controlled trials on metformin published between 2022 and 2024."*
- *"Show me papers that cite PMID 28375731."*
- *"List recent papers by Jennifer Doudna."*

**`entity_analysis_agent` (PubTator3, free):**
- *"What genes and diseases are mentioned in PMID 28375731?"*
- *"What chemicals are known to treat diabetes mellitus?"*
- *"Find the PubTator3 entity ID for BRCA1, then list genes it interacts with."*

**`deep_research_agent` (BigQuery, paid — only if provisioned):**
- *"Semantically search PMC for machine-learning approaches to predicting drug interactions."* (~$0.08)
- *"Search the full text of PMC for articles mentioning 'CRISPR Cas9 off-target effects'."* (~$0.62 — heads up)

**Multi-step delegation (coordinator chains specialists):**
- *"Find the top 3 papers on CRISPR Cas9 from 2024, then list the genes mentioned in each."*

## 6. Deploy to Vertex AI Agent Engine

You need a **GCS staging bucket in the same region** as your Agent
Engine deployment (Agent Engine itself is regional — pick one that
supports it, e.g. `us-central1`).

```bash
PROJECT=YOUR_PROJECT_ID
REGION=us-central1
BUCKET=gs://${PROJECT}-adk-staging

# One-time: create the staging bucket
gsutil mb -l $REGION $BUCKET

# Deploy
adk deploy agent_engine pubmed_agent \
    --project=$PROJECT \
    --region=$REGION \
    --staging_bucket=$BUCKET \
    --display_name="PubMed Research Agent"
```

The CLI prints the deployed agent's resource name on success
(`projects/.../reasoningEngines/...`). Test it from the Vertex AI
console **Agent Engine → Sessions** page, or programmatically via
`vertexai.agent_engines.get(...)`.

> If you also want the deployed agent to use BigQuery tools, make sure
> the Agent Engine service account in your project has
> `roles/bigquery.user` on the project. The default Reasoning Engine
> service agent is granted Vertex AI access automatically.

## Project layout

```
pubmed_agent/
├── __init__.py
├── agent.py                      # root_agent (coordinator)
├── .env                          # GOOGLE_GENAI_USE_VERTEXAI, project, location
├── requirements.txt
├── README.md
├── test_agent.py                 # tool smoke tests + suggested LLM queries
├── sub_agents/
│   ├── __init__.py
│   ├── literature_search.py      # E-utilities specialist
│   ├── deep_research.py          # BigQuery specialist (gated)
│   └── entity_analysis.py        # PubTator3 specialist
└── tools/
    ├── __init__.py
    ├── api_client.py             # async HTTP / BQ client
    ├── eutils_tools.py           # ADK FunctionTool wrappers
    ├── bigquery_tools.py
    └── pubtator_tools.py
```

## Troubleshooting

- **`pyOpenSSL` not found** when running BigQuery tools — install it:
  `pip install pyOpenSSL`. Already in `requirements.txt`; this only bites
  if you skipped the install step.
- **`Permission denied` from BQ remote model** right after IAM grant —
  IAM bindings can take 30–60s to propagate. Wait and retry.
- **`deep_research_agent` missing from the dropdown** — `GOOGLE_CLOUD_PROJECT`
  is unset, or BigQuery is unavailable. The coordinator falls back to
  keyword search and tells the user.
- **`adk deploy` complains about the staging bucket** — the bucket must
  exist and be in the same region you pass to `--region`.
