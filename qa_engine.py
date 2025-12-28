from __future__ import annotations
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from collections import defaultdict
import re

import numpy as np

from config import (
    PDF_PATH,
    INDEX_FILE,
    META_FILE,
    TOP_K,
    SCORE_THRESHOLD,
    CONFIDENCE_CLARIFY_THRESHOLD,
    EMBEDDING_MODEL_NAME,
    EN_TO_UR_MODEL,
    UR_TO_EN_MODEL,
    DEFAULT_NOT_FOUND_UR,
    DEFAULT_NOT_FOUND_EN,
    CLARIFY_UR,
    CLARIFY_EN,
)
from pdf_loader import load_pdf_text
from text_splitter import split_pages_into_chunks
from embeddings import EmbeddingModel
from vector_store import FAISSStore
from translator import Translator
from language_detector import LanguageDetector
from question_rewriter import QuestionRewriter
from question_normalizer import QuestionNormalizer
from ambiguity_checker import AmbiguityChecker


class QASystem:
    def __init__(
        self,
        store: FAISSStore,
        embedder: EmbeddingModel,
        translator: Translator,
        normalizer: QuestionNormalizer,
        ambiguity: AmbiguityChecker,
    ) -> None:
        self.store = store
        self.embedder = embedder
        self.translator = translator
        self.normalizer = normalizer
        self.ambiguity = ambiguity

    def answer(self, question: str, language: str = "urdu") -> Tuple[str, Optional[str]]:
        # 1) Normalize & rewrite question to formal Urdu
        q_ur, detected_lang = self.normalizer.normalize(question)

        # 2) Ambiguity check
        ambiguous, _reason = self.ambiguity.check(q_ur)
        if ambiguous:
            return (CLARIFY_EN if language == "english" else CLARIFY_UR), None

        q_vec = self.embedder.encode_one(q_ur, normalize=True).astype(np.float32)
        results = self.store.search(q_vec, top_k=TOP_K)

        # Confidence control: if top score is too low, ask to clarify
        best_score = results[0][0] if results else 0.0
        if best_score < CONFIDENCE_CLARIFY_THRESHOLD:
            return (CLARIFY_EN if language == "english" else CLARIFY_UR), None

        # Apply strict score threshold for answerability
        filtered = [(s, t, m) for s, t, m in results if s >= SCORE_THRESHOLD]
        if not filtered:
            return (DEFAULT_NOT_FOUND_EN if language == "english" else DEFAULT_NOT_FOUND_UR), None

        answer_ur = synthesize_answer_urdu(q_ur, filtered)
        if not answer_ur.strip():
            # Fall back to the top chunk directly (still from book)
            answer_ur = filtered[0][1].strip()

        # Build source reference
        pages = sorted({m.get("page") for _, _, m in filtered if m.get("page")})
        if not pages:
            source = None
        elif len(pages) == 1:
            source = f"Page {pages[0]}"
        else:
            source = "Pages " + ", ".join(map(str, pages))

        if language == "english":
            ans_en = self.translator.ur_to_en(answer_ur)
            return ans_en, source
        return answer_ur, source


def init_pipeline_if_needed(pdf_path: Path, index_file: Path, meta_file: Path) -> QASystem:
    # Initialize embedder first to know the dimension
    embedder = EmbeddingModel(EMBEDDING_MODEL_NAME)
    dim = embedder.model.get_sentence_embedding_dimension()

    if index_file.exists() and meta_file.exists():
        store = FAISSStore.load(index_file, meta_file)
    else:
        # Build index from PDF
        pages = load_pdf_text(pdf_path)
        chunks = split_pages_into_chunks(pages)
        texts = [c["text"] for c in chunks]
        metas = [{"page": c["page"], "chunk_id": c["chunk_id"]} for c in chunks]
        vecs = embedder.encode(texts, normalize=True).astype(np.float32)
        store = FAISSStore(dim)
        store.add(vecs, texts, metas)
        store.save(index_file, meta_file)

    translator = Translator(EN_TO_UR_MODEL, UR_TO_EN_MODEL)
    detector = LanguageDetector()
    rewriter = QuestionRewriter()
    normalizer = QuestionNormalizer(detector=detector, translator=translator, rewriter=rewriter)
    ambiguity = AmbiguityChecker()
    return QASystem(store=store, embedder=embedder, translator=translator, normalizer=normalizer, ambiguity=ambiguity)


# ---- Answer synthesis (extractive, conservative) ----

_SENT_SPLIT_RE = re.compile(r"([\.\!\?\u06D4])")  # . ! ? Urdu full stop 
_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[\.,!\?\-:\u06D4\u061F\u060C\(\)\[\]\{\}\"\']")


def tokenize_basic(text: str) -> List[str]:
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    if not text:
        return []
    return text.split(" ")


def split_sentences(text: str) -> List[str]:
    # Split by sentence enders while keeping content
    parts = _SENT_SPLIT_RE.split(text)
    if not parts:
        return [text]
    sents: List[str] = []
    cur = ""
    for p in parts:
        if _SENT_SPLIT_RE.fullmatch(p):
            cur += p
            sents.append(cur.strip())
            cur = ""
        else:
            cur += p
    if cur.strip():
        sents.append(cur.strip())
    return [s for s in sents if s]


def sentence_overlap_score(q_tokens: set[str], sentence: str) -> int:
    s_tokens = set(tokenize_basic(sentence))
    return len(q_tokens.intersection(s_tokens))


def synthesize_answer_urdu(question_ur: str, results: List[Tuple[float, str, Dict]]) -> str:
    q_tokens = set(tokenize_basic(question_ur))

    # Rank candidate sentences from top chunks by lexical overlap
    candidates: List[Tuple[int, str]] = []  # (score, sentence)
    for score, chunk_text, _meta in results:
        for sent in split_sentences(chunk_text):
            if not sent.strip():
                continue
            s = sentence_overlap_score(q_tokens, sent)
            if s > 0:
                candidates.append((s, sent.strip()))

    if not candidates:
        # If no overlap match, try returning a concise start of the top chunk
        top_text = results[0][1].strip()
        return top_text[:600]

    # Take top N sentences
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = []
    total_len = 0
    for _, sent in candidates[:8]:
        if sent in selected:
            continue
        selected.append(sent)
        total_len += len(sent)
        if total_len >= 600:
            break

    # Join with spaces; stays strictly within retrieved text
    return " ".join(selected).strip()
