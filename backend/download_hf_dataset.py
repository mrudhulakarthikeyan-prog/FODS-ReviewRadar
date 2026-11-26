"""Download a small public Amazon product-review dataset for first-run model training."""
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

DATASET_ID = "haoxianc/srinandanv_amazon-product-reviews"
API_URL = "https://datasets-server.huggingface.co/parquet"
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "dataset"
OUT_CSV = DATA_DIR / "public_product_reviews.csv"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_CSV.exists() and OUT_CSV.stat().st_size > 100_000:
        print(f"Using downloaded training data: {OUT_CSV}")
        return str(OUT_CSV)

    print("[1/3] Connecting to the public product-review dataset...")
    response = requests.get(API_URL, params={"dataset": DATASET_ID}, timeout=45)
    response.raise_for_status()
    parquet_files = response.json().get("parquet_files", [])
    train_files = [x for x in parquet_files if x.get("split") == "train"]
    if not train_files:
        raise RuntimeError("The public dataset did not provide a training file. Please retry with internet access.")

    file_info = train_files[0]
    parquet_url = file_info["url"]
    parquet_path = DATA_DIR / "public_product_reviews.parquet"
    print("[2/3] Downloading the review data (about 21 MB)...")
    with requests.get(parquet_url, stream=True, timeout=(30, 180)) as download:
        download.raise_for_status()
        total = int(download.headers.get("content-length", 0))
        received = 0
        with open(parquet_path, "wb") as output:
            for chunk in download.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)
                    received += len(chunk)
                    if total:
                        print(f"  Downloaded {received / total:.0%}", end="\r", flush=True)
    print("\n[3/3] Preparing review text and sentiment labels...")
    frame = pd.read_parquet(parquet_path)
    text_col = "Text" if "Text" in frame.columns else "cleaned_review"
    label_col = "sentiment_category"
    if text_col not in frame.columns or label_col not in frame.columns:
        raise RuntimeError(f"Dataset columns were different than expected: {list(frame.columns)}")
    frame = frame[[text_col, label_col]].rename(columns={text_col: "review_text", label_col: "sentiment"})
    frame["review_text"] = frame["review_text"].fillna("").astype(str).str.strip()
    frame["sentiment"] = frame["sentiment"].astype(str).str.strip().str.title()
    frame = frame[frame["sentiment"].isin(["Positive", "Negative", "Neutral"])]
    frame = frame[frame["review_text"].str.len() >= 3].drop_duplicates(subset=["review_text"])
    frame.to_csv(OUT_CSV, index=False, encoding="utf-8")
    info = {
        "dataset": DATASET_ID,
        "source": f"https://huggingface.co/datasets/{DATASET_ID}",
        "license": "MIT (dataset card attribution: Sri Nandan V)",
        "rows": int(len(frame)),
        "label_counts": {k: int(v) for k, v in frame["sentiment"].value_counts().items()},
        "text_field": text_col,
        "label_field": label_col,
    }
    (DATA_DIR / "DATASET_INFO.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    (DATA_DIR / "DATASET_README.txt").write_text(
        "ReviewRadar training dataset\n\n"
        f"Source: {info['source']}\nLicense: {info['license']}\n"
        f"Rows prepared: {len(frame)}\n\n"
        "This public dataset is used only to train the initial text classifier. "
        "It is not shown as customer activity in the dashboard. The dashboard starts empty "
        "and displays only reviews uploaded by the website user.\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(frame):,} labelled reviews.")
    print("Class distribution:", info["label_counts"])
    return str(OUT_CSV)


if __name__ == "__main__":
    try:
        print(main())
    except Exception as exc:
        print("\nCould not download the training dataset:", exc)
        print("Check your internet connection and run START_REVIEWRADAR.bat again.")
        sys.exit(1)
