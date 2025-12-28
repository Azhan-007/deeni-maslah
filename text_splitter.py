from typing import List, Dict
from config import CHUNK_SIZE, CHUNK_OVERLAP


def split_pages_into_chunks(pages: List[tuple]) -> List[Dict]:
    """
    Split page texts into overlapping character chunks.

    Input: list of tuples (page_number, text)
    Output: list of dicts with keys: 'text', 'page', 'chunk_id'
    """
    chunks: List[Dict] = []
    chunk_id = 0
    for page_num, text in pages:
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "chunk_id": chunk_id,
                })
                chunk_id += 1
            if end == len(text):
                break
            start = end - CHUNK_OVERLAP
            if start < 0:
                start = 0
    return chunks
