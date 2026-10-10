"""SQL validation of the model's training table, loaded into an in-memory SQLite database."""
import sqlite3

import pandas as pd
import pytest

from tests.conftest import SUT

pytestmark = pytest.mark.data


@pytest.fixture(scope="module")
def db():
    con = sqlite3.connect(":memory:")
    pd.read_csv(SUT / "data" / "features.csv").to_sql("features", con, index=False)
    yield con
    con.close()


def q(db, sql):
    return db.execute(sql).fetchone()[0]


def test_d01_row_count_matches_documented_356(db):
    assert q(db, "SELECT COUNT(*) FROM features") == 356


def test_d02_encounter_id_is_unique(db):
    assert q(db, "SELECT COUNT(*) - COUNT(DISTINCT encounter_id) FROM features") == 0


def test_d03_no_nulls_in_model_columns(db):
    cols = ["age_at_encounter", "gender", "length_of_stay_days", "prior_admissions_365d",
            "condition_count", "medication_count", "total_claim_cost", "readmitted_30d"]
    for c in cols:
        assert q(db, f"SELECT COUNT(*) FROM features WHERE {c} IS NULL") == 0, c


def test_d04_values_within_the_ranges_the_app_accepts(db):
    assert q(db, "SELECT COUNT(*) FROM features WHERE age_at_encounter NOT BETWEEN 0 AND 100") == 0
    assert q(db, "SELECT COUNT(*) FROM features WHERE length_of_stay_days NOT BETWEEN 0 AND 30") == 0
    assert q(db, "SELECT COUNT(*) FROM features WHERE total_claim_cost < 0") == 0


def test_d05_label_is_binary_and_rate_is_about_17_percent(db):
    assert q(db, "SELECT COUNT(*) FROM features WHERE readmitted_30d NOT IN (0, 1)") == 0
    assert 0.15 <= q(db, "SELECT AVG(readmitted_30d) FROM features") <= 0.19


def test_d06_gender_is_binary(db):
    assert q(db, "SELECT COUNT(*) FROM features WHERE gender NOT IN (0, 1)") == 0


@pytest.mark.xfail(strict=True, reason="BUG-002 root cause: one gender group has only 2 positive cases in the training data")
def test_d07_each_gender_group_has_enough_positive_cases(db):
    rows = db.execute("SELECT gender, SUM(readmitted_30d) FROM features GROUP BY gender").fetchall()
    assert all(pos >= 10 for _, pos in rows), rows
