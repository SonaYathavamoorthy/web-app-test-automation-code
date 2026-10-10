"""API-level tests for the JSON prediction service (status codes, schema, validation)."""
import pytest

from tests.conftest import BASE

pytestmark = pytest.mark.api


@pytest.fixture(scope="module")
def client():
    from sut.src.api import app
    app.config["TESTING"] = True
    return app.test_client()


def test_a01_health_returns_200_and_model_name(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_a02_valid_request_returns_200_with_schema(client):
    r = client.post("/predict", json=BASE)
    body = r.get_json()
    assert r.status_code == 200
    assert set(body) == {"risk", "flagged"}
    assert 0 <= body["risk"] <= 1
    assert isinstance(body["flagged"], bool)


def test_a03_api_matches_direct_model_prediction(client, predict):
    r = client.post("/predict", json={**BASE, "length_of_stay_days": 10})
    assert r.get_json()["risk"] == pytest.approx(predict(length_of_stay_days=10), abs=0.0001)


@pytest.mark.parametrize("missing", list(BASE))
def test_a04_missing_field_returns_422_naming_it(client, missing):
    body = {k: v for k, v in BASE.items() if k != missing}
    r = client.post("/predict", json=body)
    assert r.status_code == 422
    assert missing in r.get_json()["fields"]


@pytest.mark.parametrize("field,value", [("age_at_encounter", -1), ("age_at_encounter", 101),
                                        ("gender", 2), ("total_claim_cost", -500),
                                        ("total_claim_cost", 99_999_999_999)])
def test_a05_out_of_range_values_return_422(client, field, value):
    r = client.post("/predict", json={**BASE, field: value})
    assert r.status_code == 422
    assert field in r.get_json()["fields"]


@pytest.mark.parametrize("value", ["55", None, True, [55]])
def test_a06_wrong_type_returns_422(client, value):
    r = client.post("/predict", json={**BASE, "age_at_encounter": value})
    assert r.status_code == 422


def test_a07_non_json_body_returns_400(client):
    r = client.post("/predict", data="not json", content_type="text/plain")
    assert r.status_code == 400


def test_a08_wrong_method_returns_405(client):
    assert client.get("/predict").status_code == 405


def test_a09_unknown_route_returns_404(client):
    assert client.get("/nope").status_code == 404
