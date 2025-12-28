from functools import lru_cache
from transformers import pipeline


class Translator:
    def __init__(self, en_to_ur_model: str, ur_to_en_model: str) -> None:
        self._en2ur_name = en_to_ur_model
        self._ur2en_name = ur_to_en_model
        self._en2ur = None
        self._ur2en = None

    def _get_en2ur(self):
        if self._en2ur is None:
            self._en2ur = pipeline("translation", model=self._en2ur_name)
        return self._en2ur

    def _get_ur2en(self):
        if self._ur2en is None:
            self._ur2en = pipeline("translation", model=self._ur2en_name)
        return self._ur2en

    def en_to_ur(self, text: str) -> str:
        if not text:
            return text
        pipe = self._get_en2ur()
        out = pipe(text, max_length=512)
        return out[0]["translation_text"].strip()

    def ur_to_en(self, text: str) -> str:
        if not text:
            return text
        pipe = self._get_ur2en()
        out = pipe(text, max_length=512)
        return out[0]["translation_text"].strip()
