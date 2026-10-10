# IncidentIQ - Enterprise Local Incident Analytics & Reporting Platform
URL - https://incident-iq-6xew.onrender.com
**IncidentIQ** is a complete, functional, local-first operational incident analytics and reporting platform built for corporate Windows environments with strict air-gap and network constraints.

Users can query incident data in natural language (via typed input or microphone speech recognition) and receive verified tabular datasets, executive KPIs, interactive charts, analytical insights, recurring pattern fingerprints, root-cause context, and instant downloadable PDF/Excel reports—**running 100% locally with zero cloud dependencies, zero external APIs, and zero large local LLMs**.

---

## Key Highlights & Architecture

- **Zero External APIs / Zero Cloud**: Operates completely offline on a corporate laptop behind Zscaler or strict firewalls. No OpenAI, Azure, AWS, Gemini, or external speech APIs.
- **Single-File SQLite Lakehouse**: Single local database (`data/warehouse/incidentiq.db`) with full B-tree indexes and WAL mode for high-throughput reads (under 30 ms query latency).
- **Realistic Enterprise Dataset**: Over 1,280 internally-consistent incident records spanning applications (AWS, Payment Gateway, Auth Gateway, SAP ERP, Kafka, Billing, CRM, Active Directory), services, severity levels, SLAs, MTTR metrics, and root causes.
- **Natural Language Query Engine**:
  - Deterministic entity extraction & Scikit-learn TF-IDF intent classification.
  - Resolves temporal expressions ("yesterday", "last week", "this quarter", "last month", "Q3", "last 30 days").
  - Query Understanding Panel displaying Intent, Entities, Metric, Data Source, and Execution Latency.
- **Voice Microphone Input**:
  - Integrated speech recognition button (standard enterprise `Mic` icon) with states ("Listening...", "Processing...", "Transcription complete").
  - Works natively offline via client-side Web Speech API with backend audio decoding fallback. Graceful degradation to typed search if mic permissions are denied.
- **Mandatory Direct Query Result PDF**:
  - Immediate **[Download Result as PDF]** button alongside every natural language analytical result.
  - Locally compiled using **ReportLab** with running headers, query interpretation, KPI blocks, vector bar charts, and paginated incident tables.
- **Advanced Differentiating Analytics**:
  - **What Changed Since Yesterday?**: Real-time delta calculations on incident volume %, critical alert shifts, top application swings, and SLA breaches.
  - **Incident Fingerprints**: TF-IDF & Cosine Similarity clustering assigning signatures (`RP-014: AWS + Timeout + Payment + API`) with frequency tracking and trend trajectories.
  - **Incident Story Drill-Down**: 5-stage lifecycle timeline (Created &rarr; Assigned &rarr; Investigation &rarr; Root Cause Identified &rarr; Resolved) and correlated incident matching.
  - **Severity vs Operational Impact Matrix**: Scatter visualization mapping severity against multi-factor calculated impact scores (1-100).
- **Local MCP-Compatible Data Access Layer**:
  - 7 standardized local analytical tools (`get_incident_schema`, `search_incidents`, `get_incident_metrics`, `get_application_metrics`, `get_trend_metrics`, `get_recurring_patterns`, `get_root_cause_context`).
- **Single-Server Production Serving**:
  - FastAPI serves both the JSON API and the compiled React production SPA bundle from a single lightweight Python process on `http://127.0.0.1:8000`. No Node.js backend processes remain running in production.

---

## Directory Structure

```
IncidentIQ/
├── backend/
│   ├── analytics/          # What Changed, Fingerprinting, Incident Story, Impact Matrix
│   ├── api/                # FastAPI modular routes (nlp, analytics, incidents, patterns, reports, mcp)
│   ├── database/           # SQLite connection, WAL mode, queries
│   ├── mcp/                # Local MCP tool registry and JSON-RPC dispatcher
│   ├── models/             # Pydantic schemas
│   ├── nlp/                # Date parser, entity extractor, intent classifier, query planner, engine
│   ├── reporting/          # ReportLab PDF generator, OpenPyXL Excel generator, CSV generator
│   ├── semantic_layer/     # Semantic metadata cache and entity resolver
│   └── main.py             # FastAPI app with static React SPA mounting
│
├── data/
│   ├── raw/                # Data Lake layer (applications.csv, services.csv, incidents.csv)
│   ├── processed/          # Cleaned CSV layer (incidents_clean.csv)
│   └── warehouse/          # SQLite warehouse (incidentiq.db with B-tree indexes)
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Header, Sidebar, IncidentStoryDrawer, WhatChangedWidget
│   │   ├── pages/          # Dashboard, NLAnalytics, Explorer, Trends, Patterns, Impact, Reports, System
│   │   └── services/       # Axios API client
│   └── dist/               # Production compiled React bundle
│
├── semantic/
│   ├── glossary.json       # Domain glossary and synonym library
│   ├── mappings.json       # Entity, severity, status, and attribute mappings
│   └── metrics.json        # Formal metrics definitions (MTTR, SLA Breach Rate)
│
├── scripts/
│   ├── generate_dataset.py # Realistic enterprise dataset synthesizer
│   ├── init_warehouse.py   # Warehouse schema, indexer, and ETL runner
│   ├── test_nlp_queries.py # Benchmark NL query test suite
│   ├── test_api_endpoints.py # Automated API endpoint test suite
│   └── verify_system.py    # Complete 16-point E2E validation script
│
├── requirements.txt        # Python dependencies
├── start.bat               # Single-command launcher for Windows
└── README.md
```

---

## Quick Start (Windows)

### Option 1: Single-Command Launch (`start.bat`)
Double-click `start.bat` or run:
```cmd
start.bat
```
This automatically:
1. Validates the Python environment.
2. Checks the local SQLite warehouse (seeds if missing).
3. Verifies the compiled React frontend bundle.
4. Starts FastAPI at `http://127.0.0.1:8000`.
5. Launches your default web browser to the application.

### Option 2: Manual Start
To run backend and frontend during development:
```cmd
# Terminal 1 - FastAPI Backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Vite Frontend (Optional for dev editing)
cd frontend
npm run dev
```

---

## Tested Benchmark Queries

The following benchmark queries execute with sub-35ms latencies and verified local results:
1. `"What incidents were reported yesterday?"` &rarr; 10 records found.
2. `"Show all critical incidents from last week."` &rarr; 2 records found.
3. `"Which applications generated the most incidents this quarter?"` &rarr; AWS Cloud Infrastructure ranked top (189 incidents).
4. `"Show AWS incidents from last month."` &rarr; 75 AWS incidents in August 2026.
5. `"Which applications have the highest SLA breaches?"` &rarr; AWS (71 breaches), Payment Gateway (64 breaches).
6. `"Identify recurring incidents."` &rarr; 6 chronic patterns (RP-014, RP-008, RP-003, RP-022, RP-019, RP-005).
7. `"What are the most common root causes?"` &rarr; Categorical breakdown (Storage, Infrastructure Limits, Database Contention).
8. `"Which services have the longest resolution time?"` &rarr; Azure AD Connect Agent (710 min MTTR).
9. `"Show me unresolved critical incidents."` &rarr; 3 active P1 tickets requiring mitigation.

---

## Verification

Run the comprehensive test suite at any time:
```cmd
python scripts/verify_system.py
```
All 16/16 verification checks validate 100% offline functionality, ReportLab PDF generation, OpenPyXL workbooks, SQLite indexing, and local MCP tool invocation.
