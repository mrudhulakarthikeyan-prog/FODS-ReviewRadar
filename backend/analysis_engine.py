"""Explainable review insights derived only from uploaded customer review text."""
import re
from collections import Counter, defaultdict

ASPECTS = {
    "Effectiveness & results": ["work", "works", "worked", "effective", "effectiveness", "result", "results", "growth", "grow", "grew", "thicker", "longer", "fuller", "improvement", "visible", "length", "volume", "lift"],
    "Application & usability": ["apply", "application", "applicator", "wand", "easy", "use", "using", "sticky", "lightweight", "texture", "consistency", "clumpy", "clumping"],
    "Packaging": ["packaging", "package", "bottle", "container", "leak", "leaking", "cap", "seal", "dispenser"],
    "Price & value": ["price", "cost", "expensive", "cheap", "value", "worth", "money", "affordable"],
    "Comfort & safety": ["irritation", "irritate", "burn", "burning", "itch", "itchy", "redness", "sensitive", "safe", "comfortable", "reaction"],
    "Wear & removal": ["waterproof", "smudge", "smudging", "lasting", "long-lasting", "remove", "removal", "remover", "wash", "wear", "day"],
    "Quality": ["quality", "damaged", "broken", "defective", "smell", "odor", "fragrance", "authentic", "original", "fake"],
}
POSITIVE = set("""love loved lovely excellent amazing great good nice perfect recommend recommended effective works worked useful easy lightweight visible better best happy satisfied smooth healthy fuller longer thicker improvement worth affordable beautiful soft comfortable value favorite favourite nice""".split())
NEGATIVE = set("""bad worst poor disappointing disappointed waste useless ineffective doesn't didnt not never hardly weak expensive costly irritating irritation itchy burning burn redness damaged broken defective fake late difficult hard clumpy clumping smudge smudges dry drying""".split())
NEGATION = {"not", "no", "never", "hardly", "isnt", "wasnt", "doesnt", "didnt", "without"}
STOP = set("""the and a an of to it is this that in for on with as was but be by or at from are has have had were its my we they you their our so if me him her them us very i am been being product products mascara review reviews use using used get got one really also much just can could would should will dont doesn't did not no yes im ive its than then there here after before about because while when where who what which all any some more most less too very makes badly lashes lash mascara days day coat coats""".split())
GENERIC = set("""good great nice bad best product products thing things item items review reviews really very much one""".split())

def _tokens(text):
    return re.findall(r"[a-z']+", (text or "").lower())

def lexical_polarity(text):
    tokens = _tokens(text)
    score = 0
    for i, word in enumerate(tokens):
        negated = any(t in NEGATION for t in tokens[max(0, i-3):i])
        if word in POSITIVE:
            score += -1 if negated else 1
        elif word in NEGATIVE:
            score += 1 if negated else -1
    return score

def hybrid_prediction(text, model, vectorizer):
    matrix = vectorizer.transform([text])
    label = str(model.predict(matrix)[0])
    probs = model.predict_proba(matrix)[0] if hasattr(model, "predict_proba") else None
    confidence = float(max(probs)) if probs is not None else None
    score = lexical_polarity(text)
    # Lexical correction is deliberately conservative; confidence remains model-derived unless corrected.
    if score >= 2 and label != "Positive":
        label, method = "Positive", "lexical_support"
    elif score <= -2 and label != "Negative":
        label, method = "Negative", "lexical_support"
    else:
        method = "machine_learning"
    review_needed = confidence is not None and confidence < 0.55
    return {"sentiment": label, "confidence": confidence, "method": method, "review_needed": review_needed}

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|[\n;]+", text or "") if s.strip()]

def _aspect_for_text(text):
    low = (text or "").lower()
    return [name for name, terms in ASPECTS.items() if any(re.search(r"\b" + re.escape(term) + r"\b", low) for term in terms)]

def _aspect_sentiment(text, aspect, fallback):
    terms = ASPECTS.get(aspect, [])
    relevant = []
    for sentence in _sentences(text):
        # Separate contrastive clauses so each aspect keeps its own opinion.
        clauses = re.split(r"\b(?:but|however|although|whereas)\b", sentence, flags=re.I)
        for clause in clauses:
            low = clause.lower()
            if any(re.search(r"\b" + re.escape(term) + r"\b", low) for term in terms):
                relevant.append(clause)
    score = sum(lexical_polarity(s) for s in relevant)
    if score > 0: return "Positive"
    if score < 0: return "Negative"
    return fallback or "Neutral"

def _theme_terms(rows, target_sentiment):
    counts = Counter()
    for row in rows:
        if row.get("sentiment") != target_sentiment:
            continue
        for sentence in _sentences(row.get("review_text", "")):
            tokens = [w for w in _tokens(sentence) if len(w) > 2 and w not in STOP and w not in GENERIC]
            counts.update(tokens)
            counts.update(f"{a} {b}" for a, b in zip(tokens, tokens[1:]) if a not in GENERIC and b not in GENERIC)
    return [[term, count] for term, count in counts.most_common(8) if count >= 1]

def build_insights(rows):
    analysed = [r for r in rows if r.get("sentiment")]
    aspect_stats = defaultdict(lambda: {"mentions": 0, "positive": 0, "negative": 0, "neutral": 0, "evidence": []})
    mismatches = []
    recommendations = []
    for row in analysed:
        text = row.get("review_text", "")
        sentiment = row.get("sentiment")
        for aspect in _aspect_for_text(text):
            item = aspect_stats[aspect]
            item["mentions"] += 1
            aspect_label = _aspect_sentiment(text, aspect, sentiment)
            item[aspect_label.lower()] += 1
            if len(item["evidence"]) < 3:
                sentences = [s for s in _sentences(text) if any(re.search(r"\b" + re.escape(t) + r"\b", s.lower()) for t in ASPECTS[aspect])]
                evidence = (sentences[0] if sentences else text)[:240]
                if evidence not in item["evidence"]:
                    item["evidence"].append(evidence)
        rating = row.get("rating")
        try: rating = float(rating) if rating is not None else None
        except (ValueError, TypeError): rating = None
        expected = "Positive" if rating is not None and rating >= 4 else "Negative" if rating is not None and rating <= 2 else "Neutral" if rating == 3 else None
        if expected and sentiment and expected != sentiment and rating in (1, 2, 3, 4, 5):
            mismatches.append({"rating": rating, "sentiment": sentiment, "expected_from_rating": expected, "review_text": text[:240], "product_name": row.get("product_name") or "Unspecified product"})
    aspects = []
    for name, data in sorted(aspect_stats.items(), key=lambda kv: kv[1]["mentions"], reverse=True):
        dominant = max(("positive", "negative", "neutral"), key=lambda k: data[k])
        aspects.append({"aspect": name, **data, "dominant_sentiment": dominant.title()})
    for a in aspects:
        if a["negative"] > a["positive"]:
            recommendations.append({"title": f"Review {a['aspect'].lower()}", "detail": f"{a['negative']} of {a['mentions']} detected mentions were negative. Review the customer evidence and investigate recurring issues."})
    if mismatches:
        recommendations.append({"title": "Review rating–text disagreements", "detail": f"{len(mismatches)} rated reviews differ from their text prediction. These may reflect mixed feedback, rating habits or model errors; verify them manually."})
    if not recommendations and aspects:
        top = aspects[0]
        recommendations.append({"title": f"Monitor {top['aspect'].lower()}", "detail": f"This is the most frequently mentioned aspect ({top['mentions']} mentions). Continue tracking its sentiment in future uploads."})
    return {
        "review_count": len(analysed),
        "positive_keywords": _theme_terms(analysed, "Positive"),
        "negative_keywords": _theme_terms(analysed, "Negative"),
        "aspects": aspects,
        "mismatches": mismatches[:30],
        "recommendations": recommendations,
    }
