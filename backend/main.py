import os
import shutil
import uuid
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from orchestrator import run_analysis

app = FastAPI(title="Sentinel-Edge", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    path = f"/tmp/sentinel_{uuid.uuid4()}{ext}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/api/analyze/vulnerability-detection")
async def vulnerability_detection(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    path = _save_upload(file)
    try:
        raw = run_analysis(path, "vulnerability_detection")
        data = json.loads(raw)
        return {
            "filename": file.filename,
            "findings": data.get("findings", []),
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"LLM returned non-JSON: {raw}")
    finally:
        if os.path.exists(path):
            os.remove(path)


@app.post("/api/analyze/legal-risk-scoring")
async def legal_risk_scoring(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    path = _save_upload(file)
    try:
        raw = run_analysis(path, "legal_risk_scoring")
        data = json.loads(raw)
        return {
            "filename": file.filename,
            "score": data.get("score", 0),
            "findings": data.get("findings", []),
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"LLM returned non-JSON: {raw}")
    finally:
        if os.path.exists(path):
            os.remove(path)


@app.post("/api/analyze/pii-masking")
async def pii_masking(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    path = _save_upload(file)
    try:
        raw = run_analysis(path, "pii_masking")
        data = json.loads(raw)
        return {
            "filename": file.filename,
            "pii_instances": data.get("pii_instances", []),
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"LLM returned non-JSON: {raw}")
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
