"""Behavior checks on the model itself (see docs/TEST_CASES.md). Failing expectations that are
known defects are marked xfail(strict=True) so the suite documents them and flags when they are fixed."""
import pytest

pytestmark = pytest.mark.model


def test_m01_feature_order_matches_training_metadata(metrics, model):
    assert list(metrics["feature_cols"]) == [
        "age_at_encounter", "gender", "length_of_stay_days", "prior_admissions_365d",
        "condition_count", "medication_count", "total_claim_cost"]
    assert model.n_features_in_ == len(metrics["feature_cols"])


@pytest.mark.parametrize("age", [0, 18, 55, 100])
@pytest.mark.parametrize("cost", [0, 8000, 1_000_000])
def test_m02_probability_is_between_0_and_1(predict, age, cost):
    assert 0.0 <= predict(age_at_encounter=age, total_claim_cost=cost) <= 1.0


def test_m03_same_input_gives_same_output(predict):
    assert predict() == predict()


def test_m04_all_zero_and_all_max_inputs_do_not_crash(predict):
    predict(age_at_encounter=0, gender=0, length_of_stay_days=0, prior_admissions_365d=0,
            condition_count=0, medication_count=0, total_claim_cost=0)
    predict(age_at_encounter=100, gender=1, length_of_stay_days=30, prior_admissions_365d=10,
            condition_count=20, medication_count=30, total_claim_cost=10_000_000)


def test_m05_reported_auc_is_reasonable(metrics):
    key = "random_forest" if metrics["selected_model"] == "RandomForest" else "logreg"
    assert 0.7 <= metrics[key]["auc"] <= 1.0


@pytest.mark.xfail(strict=True, reason="BUG-002: changing only gender moves risk by about 18 percentage points")
def test_m06_gender_alone_should_not_swing_risk_more_than_10_points(predict):
    assert abs(predict(gender=1) - predict(gender=0)) <= 0.10


@pytest.mark.xfail(strict=True, reason="BUG-003: longer stays lower the predicted risk (expected direction is not decreasing)")
def test_m07_longer_stay_should_not_reduce_risk(predict):
    risks = [predict(length_of_stay_days=d) for d in (0, 3, 10, 30)]
    assert all(b >= a - 0.01 for a, b in zip(risks, risks[1:]))


def test_m08_prior_admissions_effect_is_the_documented_known_limitation(predict):
    # MODEL_CARD.md already documents non-monotonic prior-admissions behavior; confirm the doc is still accurate.
    risks = [predict(prior_admissions_365d=n) for n in (0, 1, 3, 6, 10)]
    assert risks[-1] < risks[0]
