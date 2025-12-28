from transformers import pipeline
from functools import lru_cache
from config import REWRITER_MODEL


class QuestionRewriter:
    def __init__(self, model_name: str = REWRITER_MODEL) -> None:
        # text2text-generation works with T5/mT5
        self.model_name = model_name
        self._pipe = None

    def _get_pipe(self):
        if self._pipe is None:
            self._pipe = pipeline("text2text-generation", model=self.model_name)
        return self._pipe

    def rewrite_to_formal_urdu(self, text: str) -> str:
        if not text:
            return text
        prompt = (
            "ہدایات: نیچے دیے گئے سوال کو بامعنی رکھ کر درست ہجے، درست نحوی ترتیب اور باوقار اردو میں لکھیں۔ صرف سوال لکھیں۔\n"
            f"سوال: {text}\n"
            "خروج: "
        )
        pipe = self._get_pipe()
        try:
            out = pipe(prompt, max_length=128, num_beams=4)
            rewritten = out[0]["generated_text"].strip()
        except Exception:
            # Fallback: return text as-is if generation fails
            rewritten = text.strip()
        # Ensure it ends like a question
        if not rewritten.endswith("؟") and not rewritten.endswith("?"):
            rewritten = rewritten.rstrip("۔.") + "؟"
        return rewritten
