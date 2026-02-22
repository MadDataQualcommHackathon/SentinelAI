import asyncio
import uuid
import os
import shutil
import random
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# ─────────────────────────────────────────────────────────────
from backend.services.ingestion    import IngestionService
from backend.services.vector_store import VectorStore
#   from services.llm          import LLMService
#   from services.prompts      import build_prompt
#   from services.reporter     import generate_report
#
#   ingestion    = IngestionService()
#   vector_store = VectorStore()
#   llm          = LLMService()
# ─────────────────────────────────────────────────────────────

# ── MOCK: ingestion ──────────────────────────────────────────
class MockIngestion:
    def process(self, file_path: str):
        # Returns fake chunks so the pipeline runs end-to-end
        return [
            {"chunk_id": f"chunk_{i}", "text": f"sample chunk {i}", "file_type": "legal", "index": i}
            for i in range(5)
        ]

# ── MOCK: vector store ───────────────────────────────────────
class MockVectorStore:
    def retrieve(self, query: str, n: int = 3):
        return ["Relevant legal context would appear here from ChromaDB"]

    def is_ready(self):
        return False   # flip to True once build_kb.py has been run

# ── MOCK: LLM ────────────────────────────────────────────────
class MockLLM:
    SAMPLE_FINDINGS = [
        {
            "risk_level": "HIGH",
            "clause_type": "IP Assignment",
            "excerpt": "Employee assigns all inventions to company including personal time",
            "recommendation": "Negotiate carve-out for inventions unrelated to company business."
        },
        {
            "risk_level": "HIGH",
            "clause_type": "Non-Compete",
            "excerpt": "Shall not engage in competing enterprise for 3 years across North America",
            "recommendation": "Limit scope to 6 months and specific geography."
        },
        {
            "risk_level": "MED",
            "clause_type": "Indemnification",
            "excerpt": "Party shall indemnify and hold harmless with no cap on liability",
            "recommendation": "Cap indemnification at total contract value."
        },
        {
            "risk_level": "MED",
            "clause_type": "Termination",
            "excerpt": "Company may terminate immediately without cause or prior notice",
            "recommendation": "Require minimum 30-day written notice period."
        },
        {
            "risk_level": "LOW",
            "clause_type": "Governing Law",
            "excerpt": "Agreement governed by laws of Delaware",
            "recommendation": "Ensure jurisdiction is acceptable to both parties."
        },
    ]

    def analyze(self, prompt: str):
        # Returns a rotating fake finding — replace with real Nexa SDK call
        return random.choice(self.SAMPLE_FINDINGS)

    def is_loaded(self):
        return False   # flip to True once Nexa SDK model is loaded

# ── MOCK: prompt builder ─────────────────────────────────────
def mock_build_prompt(file_type, context, chunk):
    # Real version lives in services/prompts.py
    return f"[MOCK PROMPT] file_type={file_type} chunk={chunk[:40]}"

# ── MOCK: report generator ───────────────────────────────────
def mock_generate_report(findings, filename, score):
    rows = "".join(
        f"<tr><td style='color:{'red' if f['risk_level']=='HIGH' else 'orange'}'>"
        f"<b>{f['risk_level']}</b></td>"
        f"<td>{f.get('clause_type', f.get('vulnerability_type',''))}</td>"
        f"<td><code>{f.get('excerpt','')[:80]}</code></td>"
        f"<td>{f.get('recommendation','')}</td></tr>"
        for f in findings
    )
    return f"""
    <html><head><style>
      body{{font-family:Arial,sans-serif;padding:32px;background:#0f172a;color:#e2e8f0}}
      h1{{color:#60a5fa}}
      table{{width:100%;border-collapse:collapse;margin-top:24px}}
      th{{background:#1e293b;padding:10px;text-align:left;color:#94a3b8}}
      td{{padding:10px;border-bottom:1px solid #1e293b;vertical-align:top;font-size:13px}}
      .score{{font-size:48px;font-weight:bold;color:#ef4444}}
    </style></head><body>
      <p style="background:#1e3a5f;color:#60a5fa;display:inline-block;
                padding:4px 12px;border-radius:20px;font-size:12px">
        🔒 Processed 100% On-Device — Qualcomm Snapdragon X Elite NPU
      </p>
      <h1>Sentinel-Edge Report</h1>
      <p style="color:#94a3b8">File: {filename} | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
      <div class="score">{score}</div>
      <p style="color:#94a3b8">Risk Score (0=safe, 100=critical)</p>
      <table>
        <tr><th>RISK</th><th>TYPE</th><th>EXCERPT</th><th>RECOMMENDATION</th></tr>
        {rows}
      </table>
    </body></html>
    """

# ── Wire up mocks ─────────────────────────────────────────────
ingestion    = IngestionService()
vector_store = VectorStore()
llm          = MockLLM() # Still mocked until Step 3!
build_prompt = mock_build_prompt
generate_report = mock_generate_report

# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────
app = FastAPI(title="Sentinel-Edge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

jobs:    dict[str, dict] = {}
history: list[dict]      = []


# ─────────────────────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return RedirectResponse(url="/ui")
def health():
    return {
        "status":       "ok",
        "model_loaded": llm.is_loaded(),
        "kb_ready":     vector_store.is_ready(),
        "internet":     False,
        "device":       "Qualcomm Snapdragon X Elite NPU",
        "note":         "Running with mock services — swap in real services when ready"
    }


# ─────────────────────────────────────────────────────────────
# ANALYZE
# ─────────────────────────────────────────────────────────────
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    allowed = {".pdf", ".py", ".js", ".ts", ".java", ".sol", ".txt", ".go"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported")

    job_id    = str(uuid.uuid4())
    file_path = f"/tmp/sentinel_{job_id}{ext}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    jobs[job_id] = {
        "job_id":      job_id,
        "filename":    file.filename,
        "status":      "processing",
        "progress":    0,
        "findings":    [],
        "score":       0,
        "report_html": "",
        "created_at":  datetime.now().isoformat(),
    }

    asyncio.create_task(_run_analysis(job_id, file_path))
    return {"job_id": job_id, "filename": file.filename, "status": "processing"}


# ─────────────────────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────────────────────
@app.get("/api/status/{job_id}")
def status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id":   job_id,
        "status":   job["status"],
        "progress": job["progress"],
        "filename": job["filename"],
        "error":    job.get("error"),
    }


# ─────────────────────────────────────────────────────────────
# REPORT — JSON
# ─────────────────────────────────────────────────────────────
@app.get("/api/report/{job_id}")
def report(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "complete":
        raise HTTPException(status_code=202, detail="Analysis not complete yet")

    findings = job["findings"]
    return {
        "filename": job["filename"],
        "score":    job["score"],
        "summary": {
            "high": sum(1 for f in findings if f.get("risk_level") == "HIGH"),
            "med":  sum(1 for f in findings if f.get("risk_level") == "MED"),
            "low":  sum(1 for f in findings if f.get("risk_level") == "LOW"),
        },
        "findings": findings,
    }


# ─────────────────────────────────────────────────────────────
# REPORT — HTML download
# ─────────────────────────────────────────────────────────────
@app.get("/api/report/{job_id}/html", response_class=HTMLResponse)
def report_html(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "complete":
        return HTMLResponse("<p>Not ready yet</p>", status_code=202)
    return HTMLResponse(job["report_html"])


# ─────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────
@app.get("/api/history")
def get_history():
    return [
        {
            "job_id":        j["job_id"],
            "filename":      j["filename"],
            "score":         j["score"],
            "status":        j["status"],
            "created_at":    j["created_at"],
            "finding_count": len(j["findings"]),
        }
        for j in history
    ]


# ─────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────
@app.delete("/api/job/{job_id}")
def delete_job(job_id: str):
    if job_id in jobs:
        del jobs[job_id]
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Job not found")


# ─────────────────────────────────────────────────────────────
# BACKGROUND TASK
# ─────────────────────────────────────────────────────────────
async def _run_analysis(job_id: str, file_path: str):
    try:
        chunks   = ingestion.process(file_path)
        total    = len(chunks)
        findings = []

        for i, chunk in enumerate(chunks):
            # Simulate processing time so progress bar is visible in UI
            await asyncio.sleep(0.6)

            context = vector_store.retrieve(chunk["text"], n=3)
            prompt  = build_prompt(chunk["file_type"], context, chunk["text"])
            result  = llm.analyze(prompt)

            if result.get("risk_level", "NONE") != "NONE":
                findings.append(result)

            jobs[job_id]["progress"] = int((i + 1) / total * 100)

        # Sort HIGH → MED → LOW
        order = {"HIGH": 0, "MED": 1, "LOW": 2}
        findings.sort(key=lambda x: order.get(x.get("risk_level", "LOW"), 3))

        high  = sum(1 for f in findings if f.get("risk_level") == "HIGH")
        med   = sum(1 for f in findings if f.get("risk_level") == "MED")
        score = min(100, high * 20 + med * 8 + (len(findings) - high - med) * 3)

        html = generate_report(findings, jobs[job_id]["filename"], score)

        jobs[job_id].update({
            "status":      "complete",
            "progress":    100,
            "findings":    findings,
            "score":       score,
            "report_html": html,
        })

        history.insert(0, jobs[job_id].copy())
        if len(history) > 20:
            history.pop()

    except Exception as e:
        jobs[job_id].update({"status": "error", "error": str(e)})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)