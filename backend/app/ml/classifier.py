import logging
import os
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

CATEGORIES: Dict[str, list] = {
    "electricity": [
        "power", "electricity", "light", "blackout", "voltage", "wire",
        "transformer", "electric", "outage", "meter",
    ],
    "water_supply": [
        "water", "pipe", "leakage", "supply", "tap", "sewage", "drain",
        "flood", "pump", "borewell",
    ],
    "sanitation": [
        "garbage", "waste", "trash", "clean", "toilet", "hygiene", "sewage",
        "litter", "dump", "smell",
    ],
    "roads": [
        "road", "pothole", "street", "traffic", "signal", "bridge",
        "footpath", "repair", "highway", "accident",
    ],
    "public_services": [
        "hospital", "school", "police", "fire", "park", "office", "bus",
        "transport", "market", "license",
    ],
}

DEPARTMENT_MAPPING: Dict[str, str] = {
    "electricity": "Electricity Department",
    "water_supply": "Water Supply Department",
    "sanitation": "Sanitation Department",
    "roads": "Roads & Infrastructure Department",
    "public_services": "Public Services Department",
}

URGENT_KEYWORDS = [
    "urgent", "emergency", "immediate", "danger", "fire", "flood",
    "accident", "death", "critical", "severe", "help",
]

_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


class GrievanceClassifier:
    """Classify grievance text into predefined categories."""

    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None
        self._trained = False
        self.load_model()

    # ── public API ────────────────────────────────────────────────────────────

    def classify(self, text: str) -> dict:
        """Return classification result dict for *text*."""
        sentiment = self._simple_sentiment(text)

        if self._trained and self._model is not None and self._vectorizer is not None:
            category, confidence = self._ml_classify(text)
        else:
            category, confidence = self._keyword_classify(text)

        department = DEPARTMENT_MAPPING.get(category, "General Administration")
        priority = self._detect_priority(text, sentiment)

        return {
            "category": category,
            "department": department,
            "priority": priority,
            "confidence_score": round(confidence, 4),
            "sentiment_score": round(sentiment, 4),
        }

    def load_model(self) -> bool:
        """Attempt to load serialised model artefacts; return True on success."""
        try:
            import joblib

            clf_path = os.path.join(_MODELS_DIR, "classifier.pkl")
            vec_path = os.path.join(_MODELS_DIR, "vectorizer.pkl")
            if os.path.exists(clf_path) and os.path.exists(vec_path):
                self._model = joblib.load(clf_path)
                self._vectorizer = joblib.load(vec_path)
                self._trained = True
                logger.info("Loaded trained ML model from %s", _MODELS_DIR)
                return True
        except Exception as exc:
            logger.warning("Could not load ML model: %s", exc)
        self._trained = False
        return False

    @property
    def is_trained(self) -> bool:
        return self._trained

    # ── private helpers ───────────────────────────────────────────────────────

    def _ml_classify(self, text: str) -> Tuple[str, float]:
        """Use the trained sklearn pipeline to classify *text*."""
        try:
            from app.ml.preprocessor import GrievancePreprocessor
            processed = GrievancePreprocessor().preprocess_text(text)
            vec = self._vectorizer.transform([processed])
            category = self._model.predict(vec)[0]
            proba = self._model.predict_proba(vec)[0]
            confidence = float(max(proba))
            return category, confidence
        except Exception as exc:
            logger.warning("ML classification failed, using keyword fallback: %s", exc)
            return self._keyword_classify(text)

    def _keyword_classify(self, text: str) -> Tuple[str, float]:
        """Keyword-based fallback classifier."""
        lower = text.lower()
        scores: Dict[str, int] = {}
        for category, keywords in CATEGORIES.items():
            scores[category] = sum(1 for kw in keywords if kw in lower)

        best_category = max(scores, key=lambda c: scores[c])
        best_score = scores[best_category]

        if best_score == 0:
            return "public_services", 0.2

        total = sum(scores.values())
        confidence = best_score / total if total > 0 else 0.2
        return best_category, min(confidence, 0.95)

    def _detect_priority(self, text: str, sentiment_score: float) -> str:
        lower = text.lower()
        if any(kw in lower for kw in URGENT_KEYWORDS):
            return "urgent"
        if sentiment_score < -0.5:
            return "high"
        if sentiment_score < -0.2:
            return "normal"
        return "low"

    def _simple_sentiment(self, text: str) -> float:
        """Lightweight rule-based sentiment scorer returning a value in [-1, 1]."""
        positive_words = {
            "good", "great", "excellent", "fine", "nice", "happy",
            "satisfied", "thank", "appreciate", "wonderful",
        }
        negative_words = {
            "bad", "terrible", "horrible", "worst", "awful", "disgusting",
            "pathetic", "useless", "broken", "damaged", "dangerous",
            "urgent", "emergency", "critical", "severe", "death",
            "problem", "issue", "complaint", "failure", "broken",
        }
        tokens = text.lower().split()
        pos = sum(1 for t in tokens if t in positive_words)
        neg = sum(1 for t in tokens if t in negative_words)
        total = pos + neg
        if total == 0:
            return -0.1  # complaints are generally negative
        return (pos - neg) / total
