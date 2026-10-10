"""End-to-end browser tests of the Streamlit readmission app (see docs/TEST_CASES.md)."""
import pytest

from playwright.sync_api import expect

from tests.ui.conftest import choose_gender, predict_and_read, set_slider

pytestmark = pytest.mark.ui


def test_ui01_page_loads_with_title_and_disclaimer(app):
    assert app.locator("h1").inner_text() == "30-Day Readmission Risk Predictor"
    assert "not a validated clinical tool" in app.locator("body").inner_text()


def test_ui02_sidebar_shows_metrics_from_metrics_file(app, metrics):
    expect(app.locator("[data-testid=stSidebar]")).to_contain_text("Test AUC")
    side = app.locator("[data-testid=stSidebar]").inner_text()
    key = "random_forest" if metrics["selected_model"] == "RandomForest" else "logreg"
    assert metrics["selected_model"] in side
    assert str(metrics[key]["auc"]) in side
    assert f"{metrics['positive_rate'] * 100:.1f}%" in side


def test_ui03_default_inputs_match_model_oracle(app, predict):
    shown = predict_and_read(app)
    assert shown == pytest.approx(predict(), abs=0.0006)  # UI rounds to 0.1%


def test_ui04_no_result_before_button_click(app):
    assert app.locator("[data-testid=stMetric]").count() == 0


def test_ui05_changed_inputs_match_oracle(app, predict):
    set_slider(app, "Length of stay (days)", 10)
    app.get_by_label("Total claim cost ($)").fill("50000")
    app.get_by_label("Total claim cost ($)").press("Enter")
    app.wait_for_timeout(800)
    shown = predict_and_read(app)
    assert shown == pytest.approx(predict(length_of_stay_days=10, total_claim_cost=50000), abs=0.0006)


def test_ui06_gender_selection_changes_oracle_input(app, predict):
    choose_gender(app, "Male")
    shown = predict_and_read(app)
    assert shown == pytest.approx(predict(gender=1), abs=0.0006)


def test_ui07_low_risk_shows_success_message(app):
    predict_and_read(app)
    assert "Lower predicted risk" in app.locator("[data-testid=stAlert]").first.inner_text()


def test_ui08_high_risk_shows_elevated_warning(app, predict):
    # Inputs found by searching the input space; the warning is only reachable in a small corner of it.
    for label, val in [("Age at encounter", 70), ("Length of stay (days)", 15),
                       ("Prior inpatient admissions (past 365 days)", 1),
                       ("Active conditions this encounter", 0),
                       ("Active medications this encounter", 20)]:
        set_slider(app, label, val)
    choose_gender(app, "Male")
    app.get_by_label("Total claim cost ($)").fill("150000")
    app.get_by_label("Total claim cost ($)").press("Enter")
    app.wait_for_timeout(800)
    shown = predict_and_read(app)
    assert shown >= 0.5
    assert "Elevated risk" in app.locator("[data-testid=stAlert]").first.inner_text()


def test_ui09_cost_field_rejects_negative_in_widget(app):
    box = app.get_by_label("Total claim cost ($)")
    box.fill("-500")
    box.press("Enter")
    app.wait_for_timeout(800)
    assert box.get_attribute("aria-invalid") == "true"


@pytest.mark.xfail(strict=True, reason="BUG-001: negative cost is flagged invalid but a score is still shown using the old value")
def test_ui10_no_score_when_cost_is_invalid(app):
    box = app.get_by_label("Total claim cost ($)")
    box.fill("-500")
    box.press("Enter")
    app.wait_for_timeout(800)
    app.get_by_role("button", name="Predict readmission risk").click()
    app.wait_for_timeout(1500)
    assert app.locator("[data-testid=stMetric]").count() == 0


@pytest.mark.xfail(strict=True, reason="BUG-004: no upper bound or warning on claim cost; 99,999,999,999 returns a normal-looking score")
def test_ui11_absurd_cost_is_rejected_or_warned(app):
    box = app.get_by_label("Total claim cost ($)")
    box.fill("99999999999")
    box.press("Enter")
    app.wait_for_timeout(800)
    app.get_by_role("button", name="Predict readmission risk").click()
    app.wait_for_timeout(1500)
    page_text = app.locator("body").inner_text().lower()
    assert app.locator("[data-testid=stMetric]").count() == 0 or "unusual" in page_text or "warning" in page_text


def test_ui12_repeated_clicks_are_stable(app):
    first = predict_and_read(app)
    for _ in range(3):
        assert predict_and_read(app) == first
    assert app.locator("[data-testid=stException]").count() == 0
