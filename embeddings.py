from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str, device: str | None = None) -> None:
        # SentenceTransformer handles device selection; device can be 'cpu' or 'cuda'
        self.model = SentenceTransformer(model_name, device=device)

    def encode(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        vectors = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        if normalize:
            vectors = l2_normalize(vectors)
        return vectors

    def encode_one(self, text: str, normalize: bool = True) -> np.ndarray:
        vec = self.encode([text], normalize=normalize)[0]
        return vec


def l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if x.ndim == 1:
        denom = max(eps, float(np.linalg.norm(x)))
        return x / denom
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms = np.maximum(norms, eps)
    return x / norms
