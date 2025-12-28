from dataclasses import dataclass
from typing import Literal
import re

try:
    from langdetect import detect
except Exception:
    detect = None

Lang = Literal["urdu", "english", "mixed", "unknown"]


@dataclass
class LanguageDetector:
    latin_threshold: float = 0.2
    arabic_threshold: float = 0.2

    def detect(self, text: str) -> Lang:
        if not text or len(text.strip()) < 2:
            return "unknown"
        # Heuristic based on Unicode ranges
        arabic_count = len(re.findall(r"[\u0600-\u06FF]", text))
        latin_count = len(re.findall(r"[A-Za-z]", text))
        total_letters = arabic_count + latin_count
        if total_letters == 0:
            # Fallback to external detector if available
            if detect:
                try:
                    code = detect(text)
                    if code == "ur":
                        return "urdu"
                    if code.startswith("en"):
                        return "english"
                except Exception:
                    pass
            return "unknown"

        arabic_ratio = arabic_count / total_letters
        latin_ratio = latin_count / total_letters

        if arabic_ratio >= self.arabic_threshold and latin_ratio >= self.latin_threshold:
            return "mixed"
        if arabic_ratio > latin_ratio:
            return "urdu"
        return "english"
