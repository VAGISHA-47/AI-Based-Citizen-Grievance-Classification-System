import logging
import re
import string

import nltk

logger = logging.getLogger(__name__)

# Download required NLTK resources at import time
for _resource in ("punkt", "punkt_tab", "stopwords", "wordnet"):
    try:
        nltk.download(_resource, quiet=True)
    except Exception as exc:
        logger.warning("Could not download NLTK resource '%s': %s", _resource, exc)

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

ENGLISH_STOPWORDS = set(stopwords.words("english"))
_stemmer = PorterStemmer()


class GrievancePreprocessor:
    """Text preprocessing pipeline for grievance complaints."""

    def preprocess(self, text: str) -> list[str]:
        """Return list of cleaned, stemmed tokens."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        tokens = word_tokenize(text)
        tokens = [
            _stemmer.stem(tok)
            for tok in tokens
            if tok not in ENGLISH_STOPWORDS
            and tok not in string.punctuation
            and len(tok) > 2
        ]
        return tokens

    def preprocess_text(self, text: str) -> str:
        """Return preprocessed text as a single space-joined string (for sklearn)."""
        return " ".join(self.preprocess(text))

    def detect_language(self, text: str) -> str:
        """Detect language code; falls back to 'en' on any error."""
        try:
            from langdetect import detect
            return detect(text)
        except Exception:
            return "en"

    def translate_to_english(self, text: str, src_lang: str) -> str:
        """Translate *text* from *src_lang* to English; falls back to original text."""
        if src_lang == "en":
            return text
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source=src_lang, target="en").translate(text)
            return translated if translated else text
        except Exception as exc:
            logger.warning("Translation failed (%s → en): %s", src_lang, exc)
            return text
