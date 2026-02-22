import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from orchestrator import run_analysis

app = FastAPI(title="Sentinel-Edge", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_SELECTIONS = {"legal_risk_scoring", "pii_masking", "vulnerability_detection"}


def _save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    path = f"/tmp/sentinel_{uuid.uuid4()}{ext}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    selection: str = Form(...),
    prompt: str = Form(""),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if selection not in VALID_SELECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid selection '{selection}'. Valid options: {sorted(VALID_SELECTIONS)}",
        )

    path = _save_upload(file)
    try:
        data = run_analysis(path, selection, user_prompt=prompt)
        return {
            "filename": file.filename,
            "selection": selection,
            "findings": data.get("findings", []),
            "score": data.get("score", 0),
            "pii_instances": data.get("pii_instances", []),
        }
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
