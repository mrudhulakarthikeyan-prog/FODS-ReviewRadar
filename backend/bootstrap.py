"""First-run setup: fetch genuine labelled reviews, train and save the best model."""
import json
import os
from pathlib import Path

from backend.download_hf_dataset import main as download_dataset
from backend.ml.train import train_and_evaluate

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models" / "sentiment_model.pkl"
VECTORIZER = ROOT / "models" / "tfidf_vectorizer.pkl"
METRICS = ROOT / "models" / "metrics.json"


def main():
    if MODEL.exists() and VECTORIZER.exists() and METRICS.exists():
        print("A trained ReviewRadar model is already available. Skipping training.")
        print("To retrain later, delete backend/models and start ReviewRadar again.")
        return
    csv_path = download_dataset()
    print("\nTraining and evaluating Logistic Regression and Naive Bayes...")
    results = train_and_evaluate(csv_path)
    print("\nTraining complete.")
    print("Selected model:", results["best_model"])
    print("Holdout evaluation:", json.dumps(results["metrics"], indent=2))
    print("Saved model files in backend/models/")


if __name__ == "__main__":
    main()
