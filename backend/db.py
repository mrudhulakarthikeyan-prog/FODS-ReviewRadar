import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "reviewradar.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                review_text TEXT NOT NULL,
                rating REAL,
                sentiment TEXT,
                confidence REAL,
                uploaded_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                total_reviews INTEGER,
                positive INTEGER,
                negative INTEGER,
                neutral INTEGER,
                created_at TEXT NOT NULL
            )
        """)

def insert_reviews(df):
    required = {"review_text"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain a review_text column")
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    for _, row in df.iterrows():
        text = str(row.get("review_text", "")).strip()
        if not text or text.lower() == "nan":
            continue
        product = row.get("product_name", "Unspecified product")
        rating = row.get("rating")
        try:
            rating = float(rating) if rating is not None and str(rating).strip() and str(rating).lower() != "nan" else None
        except (TypeError, ValueError):
            rating = None
        rows.append((str(product) if product is not None else "Unspecified product", text, rating, None, None, now))
    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO reviews (product_name, review_text, rating, sentiment, confidence, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)
    return len(rows)

def get_summary_stats():
    with get_connection() as conn:
        row = conn.execute("""
            SELECT COUNT(*) AS total_reviews,
                   SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END) AS positive,
                   SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END) AS negative,
                   SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END) AS neutral,
                   SUM(CASE WHEN sentiment IS NULL THEN 1 ELSE 0 END) AS pending
            FROM reviews
        """).fetchone()
    return {k: int(row[k] or 0) for k in row.keys()}

def get_reviews():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, product_name, review_text, rating, sentiment, confidence, uploaded_at
            FROM reviews ORDER BY id DESC
        """).fetchall()
    return [dict(row) for row in rows]

def update_predictions(predictions):
    with get_connection() as conn:
        conn.executemany(
            "UPDATE reviews SET sentiment=?, confidence=? WHERE id=?",
            [(p["sentiment"], p.get("confidence"), p["id"]) for p in predictions]
        )

init_db()
