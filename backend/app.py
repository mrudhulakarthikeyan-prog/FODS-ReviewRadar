import os
import json
import sqlite3
import io
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from backend import db
from backend.ml.train import train_and_evaluate
from backend.analysis_engine import hybrid_prediction, build_insights

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "sentiment_model.pkl")
VEC_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

model = None
vectorizer = None

def load_model():
    global model, vectorizer
    if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VEC_PATH)
    else:
        model = vectorizer = None

def csv_upload():
    if "file" not in request.files:
        return None, (jsonify({"error": "Choose a CSV file to upload."}), 400)
    file = request.files["file"]
    if not file.filename:
        return None, (jsonify({"error": "No file selected."}), 400)
    if not file.filename.lower().endswith(".csv"):
        return None, (jsonify({"error": "Only CSV files are accepted."}), 400)
    return file, None

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_trained": os.path.exists(MODEL_PATH)})

@app.post("/api/upload_training")
def upload_training():
    file, error = csv_upload()
    if error: return error
    filename = secure_filename(file.filename)
    path = os.path.join(DATASET_DIR, filename)
    file.save(path)
    try:
        frame = pd.read_csv(path)
        if "review_text" not in frame.columns:
            return jsonify({"error": "Training CSV must contain a review_text column."}), 400
        if "sentiment" not in frame.columns and "rating" not in frame.columns:
            return jsonify({"error": "Training CSV must contain sentiment or rating."}), 400
        if "sentiment" not in frame.columns:
            rating = pd.to_numeric(frame["rating"], errors="coerce")
            frame["sentiment"] = rating.map(lambda x: "Negative" if x <= 2 else ("Neutral" if x == 3 else ("Positive" if x >= 4 else None)))
        frame["sentiment"] = frame["sentiment"].astype(str).str.strip().str.title()
        frame = frame[frame["sentiment"].isin(["Positive", "Negative", "Neutral"])]
        frame["review_text"] = frame["review_text"].fillna("").astype(str).str.strip()
        frame = frame[frame["review_text"] != ""].drop_duplicates(subset=["review_text"])
        if len(frame) < 30:
            return jsonify({"error": f"Only {len(frame)} valid labelled rows found. At least 30 are required."}), 400
        missing = {"Positive", "Negative", "Neutral"} - set(frame["sentiment"])
        if missing:
            return jsonify({"error": "Missing sentiment classes: " + ", ".join(sorted(missing))}), 400
        frame.to_csv(path, index=False)
        return jsonify({"message": "Training data uploaded and validated.", "records": int(len(frame)), "class_counts": frame["sentiment"].value_counts().to_dict()}), 200
    except Exception as exc:
        return jsonify({"error": f"Could not read training CSV: {exc}"}), 400

@app.post("/api/train")
def train():
    files = [os.path.join(DATASET_DIR, n) for n in os.listdir(DATASET_DIR) if n.lower().endswith(".csv")]
    if not files:
        return jsonify({"error": "Upload a training CSV first."}), 400
    path = max(files, key=os.path.getmtime)
    try:
        metrics = train_and_evaluate(path)
        load_model()
        return jsonify(metrics)
    except Exception as exc:
        return jsonify({"error": f"Training failed: {exc}"}), 400

@app.post("/api/upload_reviews")
def upload_reviews():
    file, error = csv_upload()
    if error: return error
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)
    try:
        frame = pd.read_csv(path)
        if "review_text" not in frame.columns:
            return jsonify({"error": "Customer review CSV must contain review_text."}), 400
        count = db.insert_reviews(frame)
        return jsonify({"message": "Customer reviews uploaded successfully.", "records": count}), 200
    except Exception as exc:
        return jsonify({"error": f"Could not process review CSV: {exc}"}), 400

@app.post("/api/run_predictions")
def run_predictions():
    load_model()
    if model is None or vectorizer is None:
        return jsonify({"error": "Train a sentiment model before analysing customer reviews."}), 400
    pending = [r for r in db.get_reviews() if not r["sentiment"]]
    if not pending:
        return jsonify({"message": "There are no unanalysed reviews.", "processed": 0}), 200
    texts = [r["review_text"] for r in pending]
    updates = []
    for row in pending:
        result = hybrid_prediction(row["review_text"], model, vectorizer)
        updates.append({"id": row["id"], "sentiment": result["sentiment"], "confidence": result["confidence"]})
    db.update_predictions(updates)
    return jsonify({"message": "Sentiment analysis completed.", "processed": len(updates)})

@app.post("/api/predict")
def predict():
    load_model()
    if model is None or vectorizer is None:
        return jsonify({"error": "Train a model before predicting sentiment."}), 400
    data = request.get_json(silent=True) or {}
    reviews = data.get("reviews", [])
    if not isinstance(reviews, list) or not reviews or not all(isinstance(x, str) and x.strip() for x in reviews):
        return jsonify({"error": "Provide a non-empty reviews list containing text."}), 400
    predictions = []
    for text in reviews:
        item = {"review": text, **hybrid_prediction(text, model, vectorizer)}
        predictions.append(item)
    return jsonify({"predictions": predictions})

@app.get("/api/stats")
def stats():
    return jsonify(db.get_summary_stats())

@app.get("/api/reviews")
def reviews():
    return jsonify({"reviews": db.get_reviews()})

@app.get("/api/insights")
def insights():
    return jsonify(build_insights(db.get_reviews()))

@app.get("/api/report/csv")
def report_csv():
    rows = db.get_reviews()
    if not rows: return jsonify({"error": "No reviews are available to export."}), 400
    frame = pd.DataFrame(rows)
    output = io.BytesIO(frame.to_csv(index=False).encode("utf-8-sig"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="reviewradar_report.csv")

@app.get("/api/report/pdf")
def report_pdf():
    rows = db.get_reviews()
    if not rows: return jsonify({"error": "No reviews are available to export."}), 400
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm)
        styles = getSampleStyleSheet()
        stats_data = db.get_summary_stats()
        story = [Paragraph("ReviewRadar - Customer Review Report", styles["Title"]), Spacer(1, 8)]
        story.append(Paragraph(f"Total reviews: {stats_data['total_reviews']} | Positive: {stats_data['positive']} | Negative: {stats_data['negative']} | Neutral: {stats_data['neutral']} | Pending: {stats_data['pending']}", styles["BodyText"]))
        story.append(Spacer(1, 12))
        table_data = [["Product", "Sentiment", "Review"]]
        for row in rows[:250]:
            snippet = (row["review_text"] or "")[:180].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            table_data.append([str(row["product_name"] or "")[:35], str(row["sentiment"] or "Pending"), Paragraph(snippet, styles["BodyText"])])
        table = Table(table_data, colWidths=[42*mm, 28*mm, 110*mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#172554")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.3,colors.lightgrey),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f8fafc")])]))
        story.append(table)
        doc.build(story)
        output.seek(0)
        return send_file(output, mimetype="application/pdf", as_attachment=True, download_name="reviewradar_report.pdf")
    except ImportError:
        return jsonify({"error": "PDF export dependency missing. Install requirements.txt again."}), 500

if __name__ == "__main__":
    load_model()
    app.run(host="127.0.0.1", port=5000, debug=False)
