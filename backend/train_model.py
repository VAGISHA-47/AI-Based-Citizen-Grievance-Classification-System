"""Top-level script to train the grievance classifier.

Run from the backend/ directory:
    python train_model.py
"""
import os
import sys

# Ensure the backend package is importable when running from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml.train import main  # noqa: E402

if __name__ == "__main__":
    main()
