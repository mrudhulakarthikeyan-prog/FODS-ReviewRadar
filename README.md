# ReviewRadar

A product-review analysis workspace with three-class sentiment prediction, product-level summaries, aspect-oriented customer insights, rating–sentiment mismatch checks and downloadable reports.

## Stack
- Frontend: React, Vite, React Router, Recharts, Axios
- Backend: Flask, SQLite, Pandas
- Machine learning: TF-IDF with a trained scikit-learn sentiment classifier

## Run on Windows
1. Install Python 3.11+ and Node.js LTS.
2. Extract the ZIP.
3. Double-click `START_REVIEWRADAR.bat`.
4. Keep the backend and frontend terminal windows open. The browser opens at `http://localhost:5173`.

## Customer review CSV
Required: `review_text`.
Optional: `product_name`, `rating` (1–5).

## Analysis features
- Three-class sentiment prediction: Positive, Negative and Neutral.
- Individual review prediction with confidence and a manual-review warning for low-confidence results.
- Product-aspect insights for effectiveness/results, application/usability, packaging, price/value, comfort/safety and quality.
- Supporting excerpts from uploaded reviews.
- Rating–sentiment mismatch flags for rated reviews.
- Review-derived improvement suggestions.
- Product comparison and CSV/PDF report exports.

## Important limitations
The model's holdout metrics describe its public training dataset and are not a guarantee of performance on every product category. Aspect extraction and rating mismatch checks are explainable heuristic aids; inspect the displayed source reviews before acting on recommendations. A rating–sentiment mismatch is a review to inspect, not proof that the customer or model is wrong.

The bundled public training dataset is separate from the customer-review database. Dashboard metrics are based on uploaded customer reviews only.

## Public dataset credit
Amazon product-review dataset mirrored by `haoxianc` on Hugging Face: https://huggingface.co/datasets/haoxianc/srinandanv_amazon-product-reviews. See the dataset card and `backend/dataset/DATASET_README.txt` for source/license details.


## Final polish update
- Refreshed the interface with a dark navy navigation rail, clearer workspace header, improved spacing, typography, cards, and responsive layouts.
- Improved insight term extraction to reduce generic filler words and surface frequent terms from positive- and negative-labelled reviews.
- Improved aspect sentiment handling for contrastive wording (for example, positive packaging feedback but negative price feedback).
- Added neutral aspect counts and clearer rating/text disagreement context.
- Confidence values remain the trained model's probability output; lexical correction does not invent or inflate a confidence score.
- All dashboard and insight counts are derived from the local uploaded review database. No sample review records or fabricated performance metrics were added.

## Run
On Windows, extract the ZIP and double-click `START_REVIEWRADAR.bat` from the `ReviewRadar` folder. Keep both terminal windows open while using `http://localhost:5173`.
