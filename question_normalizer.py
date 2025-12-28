from dataclasses import dataclass
from typing import Tuple
from language_detector import LanguageDetector
from translator import Translator
from question_rewriter import QuestionRewriter


@dataclass
class QuestionNormalizer:
    detector: LanguageDetector
    translator: Translator
    rewriter: QuestionRewriter

    def normalize(self, raw_question: str) -> Tuple[str, str]:
        """
        Returns (normalized_urdu_question, detected_language_label)
        - Detects language (urdu/english/mixed/unknown)
        - Translates English/Mixed to Urdu
        - Rewrites to formal Urdu while preserving meaning
        """
        lang = self.detector.detect(raw_question)
        text = raw_question
        if lang in ("english", "mixed"):
            text = self.translator.en_to_ur(text)
            lang = "urdu"  # after translation, treat as urdu for retrieval
        # For unknown, keep text as-is and let rewriter attempt cleaning
        normalized_urdu = self.rewriter.rewrite_to_formal_urdu(text)
        return normalized_urdu, lang
