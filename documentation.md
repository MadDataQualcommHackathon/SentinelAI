# Sentinel-Edge Documentation

> Air-gapped AI security auditor for Qualcomm Edge AI Hackathon.
> Runs 100% offline on Snapdragon X Elite NPU — zero network calls, all inference and data stay on-device.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Backend API](#backend-api)
5. [Analysis Pipeline](#analysis-pipeline)
6. [Services](#services)
7. [Prompt Templates](#prompt-templates)
8. [Frontend (Streamlit)](#frontend-streamlit)
9. [Knowledge Base](#knowledge-base)
10. [Project Structure](#project-structure)
11. [Testing](#testing)
12. [Design Decisions](#design-decisions)
13. [Scope Constraints](#scope-constraints)

---

## Quick Start

### Prerequisites

- Python 3.10+
- AnythingLLM running locally on port 3001 (with Llama-3.2-3B loaded)
- Pre-built ChromaDB knowledge base

### Setup

```bash
bash setup.sh
# Installs dependencies, pulls model, builds knowledge base
```

### Run

```bash
# Terminal 1 — Backend (port 8000)
python -m uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend (Streamlit)
streamlit run frontend.py
```

### Build Knowledge Base

```bash
cd backend && python build_cuad_kb.py
# Creates cuad_chroma_db/ from CUAD PDF dataset
```

---

## Architecture Overview

```
Streamlit Frontend (frontend.py)
        | HTTP POST (localhost:8000)
        v
FastAPI Backend (main.py → backend/main.py)
        |
        v
Orchestrator (orchestrator.py)
        |
        +---> pdf_processor.py     — PDF parsing, 1000-char chunks
        +---> chroma_query.py      — Top-3 RAG retrieval from ChromaDB
        +---> anything.py          — LLM call via AnythingLLM API
        +---> response_validator.py — JSON validation + retry (up to 3x)
        |
        v
Aggregated JSON Response → Frontend renders results
```

**Data flow for a single analysis:**

1. User uploads a PDF and selects an analysis mode in the Streamlit UI
2. Frontend POSTs the file to `/api/analyze/{mode}`
3. Backend saves the PDF, loads the corresponding prompt template
4. PDF is split into chunks (1000 chars, 100 overlap)
5. For each chunk, the top-3 matching references are retrieved from ChromaDB
6. The prompt + context + chunk are sent to the LLM via AnythingLLM
7. Response is validated as JSON; retried up to 3 times on failure
8. Per-chunk results are aggregated and returned to the frontend
9. Frontend renders risk scores, finding cards, and metrics

---

## Technology Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| LLM | Llama-3.2-3B via AnythingLLM | Local API on port 3001 |
| Embeddings | all-MiniLM-L6-v2 | 80MB, runs on CPU |
| Vector DB | ChromaDB 1.5.1 | File-based, no server process |
| Backend | FastAPI 0.129.2 + Uvicorn | Async, job-based |
| Frontend | Streamlit + Plotly | Dashboard with gauge charts |
| PDF Parsing | pdfplumber 0.11.9 | Page-by-page text extraction |
| Text Splitting | LangChain RecursiveCharacterTextSplitter | 1000-char chunks, 100-char overlap |
| Target HW | Snapdragon X Elite | 45 TOPS NPU, 32GB RAM |

---

## Backend API

### Root App (`main.py` — v3.0.0)

Wraps the backend API with an enum-based mode selector and health check.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirects to `/docs` (Swagger UI) |
| `/health` | GET | Returns `{"status": "ok"}` |
| `/api/analyze/{mode}` | POST | Runs analysis (routes to backend) |

### Backend App (`backend/main.py` — v2.0.0)

Three dedicated analysis endpoints, each accepting a PDF via multipart form upload.

#### POST `/api/analyze/legal-risk-scoring`

Analyzes contracts for risky legal clauses.

**Response:**
```json
{
  "filename": "contract.pdf",
  "score": 72,
  "findings": [
    {
      "risk_level": "HIGH",
      "clause_type": "IP Assignment",
      "excerpt": "exact quote from document",
      "recommendation": "reasoning and negotiation guidance"
    }
  ]
}
```

#### POST `/api/analyze/vulnerability-detection`

Scans documents/code for security vulnerabilities.

**Response:**
```json
{
  "filename": "app.py",
  "findings": [
    {
      "vulnerability_type": "SQL Injection",
      "severity": "HIGH",
      "excerpt": "exact problematic code",
      "recommendation": "concrete secure coding fix"
    }
  ]
}
```

#### POST `/api/analyze/pii-masking`

Detects and redacts personally identifiable information.

**Response:**
```json
{
  "filename": "report.pdf",
  "pii_instances": [
    {
      "pii_type": "SSN",
      "excerpt": "surrounding context with [REDACTED_SSN]",
      "recommendation": "how to handle or remove this PII"
    }
  ]
}
```

**CORS:** Allows `localhost:5173` and `localhost:3000` origins.

---

## Analysis Pipeline

The orchestrator (`backend/orchestrator.py`) drives the full analysis:

```
load_prompt(mode)
    → process_pdf_to_queries(pdf_path)  → [chunk1, chunk2, ...]
        → for each chunk:
            chroma.get_top_3_matches(chunk)  → [ref1, ref2, ref3]
            build message = prompt + context + chunk
            call_with_retry(call_llm, message, mode)  → validated JSON
        → _aggregate(results, mode)  → final response
```

**Aggregation logic:**

- **Legal Risk Scoring:** Averages per-chunk scores, merges all findings
- **Vulnerability Detection:** Merges all findings into a single list
- **PII Masking:** Merges all PII instances into a single list

---

## Services

### `pdf_processor.py` — PDF Chunking

```python
process_pdf_to_queries(pdf_path: str) -> list[str]
```

Extracts text page-by-page with pdfplumber, then splits using LangChain's `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 100, separators: `["\n\n", "\n", " ", ""]`).

### `chroma_query.py` — Vector Store Retrieval

```python
class ChromaQueryService:
    def get_top_3_matches(self, query_text: str) -> list[str]
```

Queries the pre-built ChromaDB for the 3 most semantically similar reference chunks. Returns formatted strings with category labels.

### `pdf_vector_store.py` — Knowledge Base Builder

```python
class PDFVectorStore:
    def build_from_directory(self, directory_path: str)
```

Loads all PDFs from a directory, chunks them, embeds with all-MiniLM-L6-v2, and persists to ChromaDB.

### `response_validator.py` — JSON Validation & Retry

```python
def call_with_retry(call_llm_fn, message, selection, max_attempts=3) -> dict
```

Wraps LLM calls with JSON parsing and schema validation. Required keys per mode:

| Mode | Required Keys |
|------|--------------|
| `legal_risk_scoring` | `score`, `findings` |
| `vulnerability_detection` | `findings` |
| `pii_masking` | `pii_instances` |

Retries up to 3 times on parse errors or missing keys.

### `anything.py` — LLM Client

```python
def call_llm(message: str) -> str
```

POSTs to the local AnythingLLM API (`localhost:3001`) workspace endpoint. Returns the text response from Llama-3.2-3B.

---

## Prompt Templates

Located in `/prompt/`. Each template instructs the LLM on output format, evaluation criteria, and severity classification.

### `legal_risk_scoring.txt`

Analyzes contract clauses for risk. Severity levels:

| Level | Criteria |
|-------|----------|
| HIGH | Uncapped liability, power imbalance, full IP surrender |
| MED | Restricted but with reasonable boundaries |
| LOW | Standard boilerplate, mutual protections |

Outputs a 0–100 risk score plus categorized findings (IP Assignment, Non-Compete, Indemnification, Termination, Limitation of Liability, Governing Law, Confidentiality, Audit Rights, Warranty, PII Detection).

### `vulnerability_detection.txt`

Identifies security vulnerabilities following OWASP/CWE standards. Process: identify inputs → trace data flow → check sanitization → categorize. Outputs findings with severity (HIGH/MED/LOW), vulnerability type, excerpt, and fix recommendation.

### `pii_masking.txt`

Detects 13+ PII types: SSN, Email, Phone, Full Name, Address, DOB, Passport, Driver's License, Bank Account, Credit Card, Medical Record Numbers, IP Addresses, Biometric Data. Redacts using `[REDACTED_{TYPE}]` tokens.

---

## Frontend (Streamlit)

`frontend.py` provides a dark-themed command center dashboard.

### Layout

**Sidebar:**
- Snapdragon X Elite badge (pink-purple gradient)
- File uploader (PDF only)
- Analysis mode selector (radio buttons)
- "INITIATE SCAN" button

**Main Panel:**
- Title: "Sentinel-Edge Command Center"
- Telemetry panel: 45 TOPS NPU Compute | Llama 3.2 3B | 0 bytes Cloud Leakage | Secure Enclave Status

### Analysis Modes

| Display Name | API Mode |
|-------------|----------|
| Legal Risk Scoring | `legal_risk_scoring` |
| PII Masking Audit | `pii_masking` |
| Vulnerability Detection | `vulnerability_detection` |

### Results Rendering

**Legal Risk Scoring:**
- Plotly gauge chart (0–100 threat score, color-coded)
- Metric cards: Critical Clauses / Medium Risk / Standard Boilerplate counts
- Finding cards sorted HIGH → MED → LOW

**Vulnerability Detection:**
- Total CWE/OWASP vectors count
- High Severity Exposures count
- Finding cards sorted by severity

**PII Masking:**
- Total PII Leaks metric
- Redaction log cards for each detected instance

### Finding Cards

Each card displays:
- Color-coded risk badge (RED = HIGH, ORANGE = MED, GREEN = LOW)
- Title (clause type / vulnerability type / PII type)
- Excerpt in a code block
- Recommendation text

### Loading State

Animated progress bar with 10 cycling status messages while the backend processes the request. Uses threading for non-blocking API calls.

---

## Knowledge Base

### Source Data

**CUAD (Contract Understanding Atticus Dataset):** Collection of legal contract PDFs covering 41 clause type definitions. Used as the RAG reference corpus for legal analysis.

### Build Process

```bash
cd backend && python build_cuad_kb.py
```

1. Loads all PDFs from the CUAD directory
2. Splits into 1000-character chunks (100-char overlap)
3. Embeds using all-MiniLM-L6-v2 sentence transformer
4. Persists to ChromaDB at `cuad_chroma_db/`

### Embedding Model

`all-MiniLM-L6-v2` — 80MB model stored locally at `./offline_embedding_model`. Runs on CPU, produces 384-dimensional embeddings. Used for both indexing and query-time retrieval.

---

## Project Structure

```
SentinelAI/
├── main.py                    # Root FastAPI app (v3.0.0)
├── frontend.py                # Streamlit dashboard
├── requirements.txt           # Root dependencies
├── setup.sh                   # One-time setup script
├── CLAUDE.md                  # Dev guidelines
├── documentation.md           # This file
│
├── backend/
│   ├── main.py                # FastAPI v2.0.0 (3 analysis endpoints)
│   ├── orchestrator.py        # Analysis pipeline coordinator
│   ├── anything.py            # AnythingLLM API client
│   ├── response_validator.py  # JSON validation + retry logic
│   ├── build_cuad_kb.py       # Knowledge base builder
│   ├── requirements.txt       # Backend dependencies
│   │
│   └── services/
│       ├── pdf_processor.py   # PDF → text chunks
│       ├── pdf_parser.py      # Raw PDF text extraction
│       ├── pdf_vector_store.py # ChromaDB builder
│       └── chroma_query.py    # Vector store query service
│
├── prompt/
│   ├── legal_risk_scoring.txt
│   ├── vulnerability_detection.txt
│   └── pii_masking.txt
│
└── test/
    └── anything.py            # AnythingLLM connectivity test
```

---

## Testing

### `test_generation.py`

Full pipeline test: PDF chunking → ChromaDB retrieval → LLM analysis → result aggregation.

```bash
python test_generation.py
```

### `test_retrieval.py`

Isolated ChromaDB query test: processes a PDF into chunks and retrieves top-3 matches for the first chunk.

```bash
python test_retrieval.py
```

### `test/anything.py`

AnythingLLM API connectivity check.

```bash
python test/anything.py
```

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM | Llama-3.2-3B via AnythingLLM | Fits 16GB RAM, NPU-native |
| Embeddings | all-MiniLM-L6-v2 | 80MB, fast, runs on CPU |
| Vector DB | ChromaDB (file-based) | Zero server, fully offline |
| Legal Dataset | CUAD (41 clause types) | Free, comprehensive legal KB |
| Code Dataset | OWASP Top 10 + CWE Top 25 | Industry standard |
| Frontend | Streamlit | Rapid prototyping, Python-native |
| Backend | FastAPI + Uvicorn | Async, minimal boilerplate |
| Database | SQLite | Built-in, zero setup |

---

## Scope Constraints

These are intentionally excluded from the MVP:

- No user authentication or multi-user support
- No cloud backup or network calls of any kind
- No Docker containerization
- No model fine-tuning or training
- PDF-only input (code file support is conceptual)
- Polling-based job status (no real-time streaming)
