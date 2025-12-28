# Deeni Q&A (Taleem-ul-Islam)

A FastAPI backend that answers questions strictly from the Urdu book "Taleem-ul-Islam" using a lightweight RAG pipeline with FAISS.

## Features
- Python + FastAPI
- PDF ingestion (PyMuPDF)
- Char-based chunking with overlap
- Multilingual embeddings (Sentence-Transformers)
- Local FAISS vector store
- Urdu/English support with Marian MT translation
- Strictly context-only answers; otherwise a clear not-found message

## Project Layout
- app.py — FastAPI entrypoint (CORS enabled)
- pdf_loader.py — Urdu PDF text extraction
- text_splitter.py — Chunking logic
- embeddings.py — Embedding model wrapper
- vector_store.py — FAISS store build/load/search
- translator.py — EN↔UR translation utilities
- qa_engine.py — Retrieval + extractive answer synthesis
- prompts.py — System prompt (for reference)
- config.py — Paths and settings
- data/Taleem-ul-Islam.pdf — Place your PDF here

## Setup
1. Ensure Python 3.10+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place the PDF file at:
- `data/Taleem-ul-Islam.pdf`

## Run
Builds the FAISS index on first start (can take a few minutes).

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Health check:
- GET http://localhost:8000/

Ask a question:
- POST http://localhost:8000/ask

```json
{
  "question": "نماز کے فرائض کیا ہیں؟",
  "language": "urdu"
}
```

or in English:

```json
{
  "question": "What are the obligatory parts of Salah?",
  "language": "english"
}
```

## Response
```json
{
  "answer": "...",
  "source": "Page 12"
}
```

If not found:
- Urdu: "اس کتاب میں اس کا واضح ذکر موجود نہیں۔"
- English: "This book does not mention this explicitly."

## Android notes
- JSON-only responses
- CORS enabled
- Keep payloads small: send concise questions

## Disclaimer
Answers are derived only from Taleem-ul-Islam. For complex issues, consult a qualified scholar.
