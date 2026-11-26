import json
import os
import sys
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
CLASSES = ["Negative", "Neutral", "Positive"]

def train_and_evaluate(csv_path):
    df = pd.read_csv(csv_path)
    if "review_text" not in df.columns:
        raise ValueError("Training CSV must contain review_text.")
    if "sentiment" not in df.columns:
        if "rating" not in df.columns:
            raise ValueError("Training CSV needs sentiment or rating.")
        ratings = pd.to_numeric(df["rating"], errors="coerce")
        df["sentiment"] = ratings.map(lambda x: "Negative" if x <= 2 else ("Neutral" if x == 3 else ("Positive" if x >= 4 else None)))
    df = df.dropna(subset=["review_text", "sentiment"]).copy()
    df["review_text"] = df["review_text"].astype(str).str.strip()
    df["sentiment"] = df["sentiment"].astype(str).str.strip().str.title()
    df = df[df["sentiment"].isin(CLASSES)]
    df = df[df["review_text"] != ""].drop_duplicates(subset=["review_text"])
    counts = df["sentiment"].value_counts()
    if len(df) < 30 or any(counts.get(c, 0) < 2 for c in CLASSES):
        raise ValueError("Need at least 30 valid rows and at least 2 examples of each sentiment class.")
    X_train, X_test, y_train, y_test = train_test_split(
        df["review_text"], df["sentiment"], test_size=0.2, random_state=42, stratify=df["sentiment"]
    )
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=30000, min_df=1, stop_words="english")
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "naive_bayes": MultinomialNB()
    }
    results = {}
    best_model, best_name, best_f1 = None, None, -1
    for name, estimator in candidates.items():
        estimator.fit(Xtr, y_train)
        pred = estimator.predict(Xte)
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision_score(y_test, pred, average="weighted", zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, pred, average="weighted", zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, pred, average="weighted", zero_division=0)), 4)
        }
        results[name] = metrics
        if metrics["f1_score"] > best_f1:
            best_model, best_name, best_f1 = estimator, name, metrics["f1_score"]
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(best_model, os.path.join(MODEL_DIR, "sentiment_model.pkl"))
    report = classification_report(y_test, best_model.predict(Xte), labels=CLASSES, output_dict=True, zero_division=0)
    payload = {
        "best_model": best_name,
        "metrics": results[best_name],
        "all_models": results,
        "training_rows": int(len(df)),
        "test_rows": int(len(y_test)),
        "class_labels": CLASSES,
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_test, best_model.predict(Xte), labels=CLASSES).tolist()
    }
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python train.py <training_csv_path>")
    print(json.dumps(train_and_evaluate(sys.argv[1]), indent=2))
