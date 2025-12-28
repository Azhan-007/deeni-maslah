import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import (
    APP_NAME,
    CORS_ORIGINS,
    INDEX_DIR,
    INDEX_FILE,
    META_FILE,
    PDF_PATH,
)
from qa_engine import QASystem, init_pipeline_if_needed


class AskRequest(BaseModel):
    question: str = Field(..., description="User question in Urdu or English")
    language: str = Field(..., description="'urdu' or 'english'")


class AskResponse(BaseModel):
    answer: str
    source: Optional[str] = None


app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa: Optional[QASystem] = None
ACTIVE_PDF_PATH: Path = PDF_PATH


@app.on_event("startup")
async def startup_event():
    # Ensure storage directory exists
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline: if FAISS index not found but PDF exists, build it.
    global qa
    global ACTIVE_PDF_PATH
    # Select PDF: prefer configured PDF, else first .pdf in data folder
    if not PDF_PATH.exists():
        try:
            from config import DATA_DIR
            candidates = sorted(Path(DATA_DIR).glob("*.pdf"))
            if candidates:
                ACTIVE_PDF_PATH = candidates[0]
        except Exception:
            pass
    try:
        qa = init_pipeline_if_needed(pdf_path=ACTIVE_PDF_PATH, index_file=INDEX_FILE, meta_file=META_FILE)
    except FileNotFoundError:
        # PDF not present yet; keep API up for health check
        qa = None
    except Exception:
        # Any other startup error should not kill the server; QA remains None
        qa = None


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if req.language.lower() not in {"urdu", "english"}:
        raise HTTPException(status_code=400, detail="language must be 'urdu' or 'english'")

    if qa is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "QA engine not initialized. Ensure the PDF exists and restart.",
                "expected_pdf_path": str(PDF_PATH.absolute()),
            },
        )

    answer, source = qa.answer(question=req.question, language=req.language.lower())
    return AskResponse(answer=answer, source=source)


@app.get("/")
async def root():
    status = {
        "app": APP_NAME,
        "pdf_present": ACTIVE_PDF_PATH.exists(),
        "index_present": INDEX_FILE.exists() and META_FILE.exists(),
        "index_dir": str(INDEX_DIR),
        "pdf_path": str(ACTIVE_PDF_PATH),
    }
    return status
