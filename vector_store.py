from __future__ import annotations
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json

import numpy as np
import faiss


class FAISSStore:
    def __init__(self, dim: int) -> None:
        # Cosine similarity supported via normalized vectors + inner product
        self.index = faiss.IndexFlatIP(dim)
        self.texts: List[str] = []
        self.metas: List[Dict] = []
        self.dim = dim

    def add(self, vectors: np.ndarray, texts: List[str], metas: List[Dict]) -> None:
        assert vectors.shape[0] == len(texts) == len(metas)
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        self.index.add(vectors)
        self.texts.extend(texts)
        self.metas.extend(metas)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, str, Dict]]:
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)
        if query_vec.dtype != np.float32:
            query_vec = query_vec.astype(np.float32)
        D, I = self.index.search(query_vec, top_k)
        scores = D[0].tolist()
        idxs = I[0].tolist()
        results: List[Tuple[float, str, Dict]] = []
        for s, idx in zip(scores, idxs):
            if idx == -1:
                continue
            results.append((float(s), self.texts[idx], self.metas[idx]))
        return results

    def save(self, index_file: Path, meta_file: Path) -> None:
        index_file.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_file))
        with meta_file.open("w", encoding="utf-8") as f:
            json.dump({
                "texts": self.texts,
                "metas": self.metas,
                "dim": self.dim,
            }, f, ensure_ascii=False)

    @classmethod
    def load(cls, index_file: Path, meta_file: Path) -> "FAISSStore":
        if not index_file.exists() or not meta_file.exists():
            raise FileNotFoundError("FAISS index or metadata not found")
        with meta_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        index = faiss.read_index(str(index_file))
        store = cls(dim=data.get("dim", index.d))
        store.index = index
        store.texts = list(data["texts"])  # preserve order
        store.metas = list(data["metas"])  # preserve order
        return store
