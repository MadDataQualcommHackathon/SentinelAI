import os
import shutil
from enum import Enum

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.orchestrator import run_analysis, FIXED_PDF_PATH

app = FastAPI(title="Sentinel-Edge", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisMode(str, Enum):
    legal_risk_scoring = "legal_risk_scoring"
    pii_masking = "pii_masking"
    vulnerability_detection = "vulnerability_detection"


# --- RESTORED REDIRECT ---
@app.get("/")
def root():
    """Redirects the base URL straight to the Swagger UI"""
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Sentinel API is running"}


@app.post("/api/analyze")
async def analyze_document(
    file: UploadFile = File(...), 
    analysis_mode: AnalysisMode = Form(...)
):
    """
    Accepts a PDF and an analysis mode enum.
    Saves the PDF to a hardcoded path and triggers the orchestrator.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with open(FIXED_PDF_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        result_dict = run_analysis(analysis_mode.value)
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis_mode": analysis_mode.value,
            "data": result_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Analysis failed: {str(e)}")
    finally:
        if os.path.exists(FIXED_PDF_PATH):
            os.remove(FIXED_PDF_PATH)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)