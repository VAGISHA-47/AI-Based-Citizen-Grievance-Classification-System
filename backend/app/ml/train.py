import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MODELS_DIR = os.path.join(_BACKEND_DIR, "models")


def load_sample_data(filepath: str) -> list:
    """Load labelled training samples from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def train_classifier(data_path: str) -> None:
    """Train TF-IDF + LogisticRegression (and MultinomialNB for comparison),
    save the best model to models/."""
    import joblib
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.feature_extraction.text import TfidfVectorizer

    from app.ml.preprocessor import GrievancePreprocessor

    print(f"Loading data from {data_path} …")
    samples = load_sample_data(data_path)

    preprocessor = GrievancePreprocessor()
    texts = [preprocessor.preprocess_text(s["text"]) for s in samples]
    labels = [s["category"] for s in samples]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # ── Logistic Regression ───────────────────────────────────────────────────
    lr = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr.fit(X_train_vec, y_train)
    lr_preds = lr.predict(X_test_vec)
    lr_acc = accuracy_score(y_test, lr_preds)
    print(f"\nLogistic Regression accuracy : {lr_acc:.4f}")
    print(classification_report(y_test, lr_preds))

    # ── Multinomial Naïve Bayes (comparison) ──────────────────────────────────
    nb = MultinomialNB()
    nb.fit(X_train_vec, y_train)
    nb_preds = nb.predict(X_test_vec)
    nb_acc = accuracy_score(y_test, nb_preds)
    print(f"Multinomial NB accuracy      : {nb_acc:.4f}")
    print(classification_report(y_test, nb_preds))

    # ── Save the better model ─────────────────────────────────────────────────
    best_model = lr if lr_acc >= nb_acc else nb
    best_name = "LogisticRegression" if lr_acc >= nb_acc else "MultinomialNB"
    print(f"\nSaving {best_name} as the production model …")

    os.makedirs(_MODELS_DIR, exist_ok=True)
    joblib.dump(best_model, os.path.join(_MODELS_DIR, "classifier.pkl"))
    joblib.dump(vectorizer, os.path.join(_MODELS_DIR, "vectorizer.pkl"))
    print(f"Model artefacts saved to {_MODELS_DIR}")


def main() -> None:
    data_path = os.path.join(_BACKEND_DIR, "sample_data.json")
    if not os.path.exists(data_path):
        print(f"ERROR: sample_data.json not found at {data_path}", file=sys.stderr)
        sys.exit(1)
    train_classifier(data_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
