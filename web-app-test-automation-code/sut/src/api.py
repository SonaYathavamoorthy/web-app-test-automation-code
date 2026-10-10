"""Small JSON prediction service wrapped around the readmission model.

Added so the model can be tested at the API level (status codes, schema,
input validation). Run:  flask --app sut.src.api run
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
METRICS = json.loads((ROOT / "models" / "metrics.json").read_text())
FEATURES = METRICS["feature_cols"]
MODEL = joblib.load(ROOT / "models" / "readmission_model.joblib")

# (min, max) allowed for each input, mirroring the Streamlit app's widgets.
LIMITS = {
    "age_at_encounter": (0, 100),
    "gender": (0, 1),
    "length_of_stay_days": (0, 30),
    "prior_admissions_365d": (0, 10),
    "condition_count": (0, 20),
    "medication_count": (0, 30),
    "total_claim_cost": (0, 10_000_000),
}

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", model=METRICS["selected_model"])


@app.post("/predict")
def predict():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="body must be a JSON object"), 400
    missing = [f for f in FEATURES if f not in body]
    if missing:
        return jsonify(error="missing fields", fields=missing), 422
    errors = {}
    for f in FEATURES:
        v = body[f]
        lo, hi = LIMITS[f]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            errors[f] = "must be a number"
        elif not lo <= v <= hi:
            errors[f] = f"must be between {lo} and {hi}"
    if errors:
        return jsonify(error="invalid values", fields=errors), 422
    row = pd.DataFrame([{f: body[f] for f in FEATURES}])
    risk = float(MODEL.predict_proba(row)[0, 1])
    return jsonify(risk=round(risk, 4), flagged=risk >= 0.5)
