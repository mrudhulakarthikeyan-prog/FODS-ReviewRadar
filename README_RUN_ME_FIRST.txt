REVIEWRADAR - QUICK START
=========================

1. Extract the complete ZIP into a normal folder (for example, Documents\ReviewRadar).
2. Make sure Python 3.11+ and Node.js LTS are installed.
3. Double-click START_REVIEWRADAR.bat.
4. On the first run, keep the internet connection on. The setup installs dependencies,
   downloads a public Amazon product-review dataset, trains Logistic Regression and
   Naive Bayes, compares them on a held-out test split, saves the better model, and
   launches the website. This first setup may take several minutes.
5. The browser opens at http://localhost:5173. Keep both terminal windows open.

AFTER FIRST RUN
---------------
Double-click START_REVIEWRADAR.bat again. The trained model and installed packages
are reused; it will not download/train again unless backend/models is deleted.

IMPORTANT
---------
- The model is trained from a public dataset, not from fabricated review records.
- The model's reported metrics are holdout evaluation results for that public dataset;
  they are not a promise of accuracy on every product or customer population.
- Public training records are kept separate from the dashboard. The dashboard begins
  empty and displays only reviews that you upload for analysis.
- For customer review CSV files, include a column named review_text. Optional columns
  include product_name and rating.
- For your own training CSV, use review_text plus sentiment (Positive/Negative/Neutral),
  or review_text plus rating (1-2 Negative, 3 Neutral, 4-5 Positive).
- Internet is required for first-time setup and public dataset download.

DATASET CREDIT
--------------
Dataset: srinandanv Amazon Product Reviews, mirrored by haoxianc on Hugging Face.
Source: https://huggingface.co/datasets/haoxianc/srinandanv_amazon-product-reviews
License: MIT, as stated on the dataset card. Attribution to original author Sri Nandan V.

LATEST ANALYSIS IMPROVEMENTS
---------------------------
- Individual predictions now combine the trained classifier with conservative
  language-cue support when the model conflicts with several clear sentiment terms.
- Low-confidence individual predictions are explicitly flagged for manual review.
- Insights now group review evidence by product aspects such as effectiveness,
  application, packaging, price/value, comfort/safety and quality.
- Rating–sentiment mismatches are highlighted when a supplied star rating differs
  from the text prediction.
- Improvement suggestions are generated from the negative aspect evidence found
  in the uploaded reviews. These are decision-support prompts, not guarantees.

The aspect and mismatch features are heuristic, explainable analysis. ReviewRadar
should be used as decision support; manually verify ambiguous reviews.
