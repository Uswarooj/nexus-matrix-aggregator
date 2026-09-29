# Nexus Matrix Aggregator

> AI-powered B2B lead-intelligence dashboard — aggregates tech-news RSS feeds and uses
> Gemini to flag articles that signal breaches, outages, or automation opportunities.

A Streamlit app that turns raw news streams into an actionable lead feed. It scans RSS feeds,
sends each new article to Gemini (`gemini-2.5-flash`) with a B2B analyst prompt, and stores
anything flagged as a lead in a local SQLite database with the model's one-line assessment.

## How it works

1. **Ingest** — Pulls the latest articles from configured RSS feeds (TechCrunch, ZDNet).
2. **Analyze** — Each new article is sent to Gemini with a structured prompt that returns
   strict JSON: `{ "is_lead": true/false, "insight": "..." }`. A lead = signs of a critical
   technical failure, data breach, system outage, cyber attack, operational bottleneck,
   legacy-system pain, or a direct need for AI / workflow automation.
3. **Store** — Leads are deduplicated by URL and persisted in SQLite (`leads_v2.db`).
4. **Display** — A live dashboard shows total leads, connected feeds, engine status, and the
   full intelligence feed with per-lead AI assessments. A sidebar button triggers a fresh crawl.

## Tech stack

- **Python** · **Streamlit** (dashboard UI)
- **Google Gemini API** (`gemini-2.5-flash`, JSON-mode responses)
- **feedparser** (RSS ingestion) · **SQLite** (lead storage, dedupe by URL)
- **python-dotenv** (local config; Streamlit secrets supported for deploys)

## Setup

```bash
git clone https://github.com/Uswarooj/nexus-matrix-aggregator.git
cd nexus-matrix-aggregator
pip install -r requirements.txt
```

Create a `.env` file (never commit it):

```
GEMINI_API_KEY=your_key_here
```

Run it:

```bash
streamlit run app.py
```

Then click **LAUNCH DYNAMIC CRAWL** in the sidebar to start ingesting and analyzing.

## Project structure

```
nexus-matrix-aggregator/
├── app.py            # Full app: ingestion, Gemini pipeline, SQLite layer, Streamlit UI
├── requirements.txt
└── .gitignore
```

## Notes

- Personal build for exploring AI-assisted lead research over public news data.
- The Gemini API key is read from environment / Streamlit secrets — no keys in code.
- Cost-conscious by design: only new, unseen articles are sent to the model.
