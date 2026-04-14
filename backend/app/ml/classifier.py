from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import settings


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    priority: str
    is_duplicate: bool
    duplicate_of_id: int | None
    similarity_score: float | None


class GrievanceClassifier:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(settings.model_name_or_path)
        self.model.eval()

    def _predict_category(self, text: str) -> tuple[str, float]:
        encoded = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
        with torch.no_grad():
            output = self.model(**encoded)
            probs = torch.softmax(output.logits, dim=-1).cpu().numpy()[0]

        max_idx = int(np.argmax(probs))
        confidence = float(probs[max_idx])

        # If a fine-tuned model is loaded, id2label is expected to represent grievance classes.
        raw_label = self.model.config.id2label.get(max_idx, "Other")
        if raw_label.upper().startswith("LABEL_"):
            if max_idx < len(settings.candidate_labels):
                return settings.candidate_labels[max_idx], confidence
            return "Other", confidence
        return str(raw_label), confidence

    def _predict_priority(self, text: str) -> str:
        lowered = text.lower()
        high_priority_tokens = {"urgent", "emergency", "accident", "fire", "flood", "hospital", "danger"}
        low_priority_tokens = {"suggestion", "feedback", "request", "information"}

        if any(token in lowered for token in high_priority_tokens):
            return "high"
        if any(token in lowered for token in low_priority_tokens):
            return "low"
        return "medium"

    def _detect_duplicate(self, text: str, existing: dict[int, str]) -> tuple[bool, int | None, float | None]:
        if not existing:
            return False, None, None

        corpus = [text] + list(existing.values())
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        top_idx = int(np.argmax(scores))
        top_score = float(scores[top_idx])
        target_id = list(existing.keys())[top_idx]

        if top_score >= settings.duplicate_threshold:
            return True, target_id, top_score
        return False, None, top_score

    def classify(self, text: str, existing: dict[int, str]) -> ClassificationResult:
        category, confidence = self._predict_category(text)
        priority = self._predict_priority(text)
        is_duplicate, duplicate_of_id, similarity = self._detect_duplicate(text, existing)

        return ClassificationResult(
            category=category,
            confidence=confidence,
            priority=priority,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
            similarity_score=similarity,
        )


classifier = GrievanceClassifier()
