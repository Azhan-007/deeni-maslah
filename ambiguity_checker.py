from dataclasses import dataclass
import re
from typing import Tuple

URDU_Q_WORDS = {
    "کیا", "کیسے", "کیونکر", "کیوں", "کب", "کہاں", "کون", "کس", "کس کا", "کس کی", "کیا حکم",
}

_punct = re.compile(r"[\.,!\?\-:\u06D4\u061F\u060C\(\)\[\]\{\}\"\']")
_ws = re.compile(r"\s+")


def _tokens(text: str):
    text = _punct.sub(" ", text)
    text = _ws.sub(" ", text).strip()
    if not text:
        return []
    return text.split(" ")


@dataclass
class AmbiguityChecker:
    min_chars: int = 6
    min_tokens: int = 2

    def check(self, question_urdu: str) -> Tuple[bool, str | None]:
        if not question_urdu or len(question_urdu.strip()) < self.min_chars:
            return True, "too_short"
        toks = _tokens(question_urdu)
        if len(toks) < self.min_tokens:
            return True, "too_few_tokens"
        # Heuristic: a valid question often includes a question mark or interrogative word
        if "؟" not in question_urdu and not any(w in question_urdu for w in URDU_Q_WORDS):
            # Allow longer statements, but prompt clarification if not interrogative
            if len(toks) < 4:
                return True, "not_interrogative"
        return False, None
