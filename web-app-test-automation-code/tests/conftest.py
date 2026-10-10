"""Shared fixtures: the model under test and an oracle that predicts directly."""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SUT = ROOT / "sut"
sys.path.insert(0, str(ROOT))

BASE = dict(age_at_encounter=55, gender=0, length_of_stay_days=3,
            prior_admissions_365d=0, condition_count=2, medication_count=3,
            total_claim_cost=8000)


@pytest.fixture(scope="session")
def metrics():
    return json.loads((SUT / "models" / "metrics.json").read_text())


@pytest.fixture(scope="session")
def model():
    return joblib.load(SUT / "models" / "readmission_model.joblib")


@pytest.fixture(scope="session")
def predict(model, metrics):
    """Oracle: risk straight from the model, bypassing the UI and API."""
    cols = metrics["feature_cols"]

    def _predict(**overrides):
        row = {**BASE, **overrides}
        return float(model.predict_proba(pd.DataFrame([row])[cols])[0, 1])

    return _predict
