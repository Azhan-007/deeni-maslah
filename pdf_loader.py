from typing import List, Tuple
from pathlib import Path
import fitz  # PyMuPDF


def load_pdf_text(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text per page from the given PDF.

    Returns a list of tuples: (page_number_1_based, text)
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    pages: List[Tuple[int, str]] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            # Extract text with blocks (layout aware). "text" extracts plain text.
            text = page.get_text("text")
            text = normalize_whitespace(text)
            pages.append((i + 1, text))
    return pages


def normalize_whitespace(text: str) -> str:
    # Collapse multiple spaces/newlines; keep Urdu punctuation.
    return "\n".join(
        line.strip()
        for line in text.replace("\r", "").split("\n")
        if line.strip()
    )
