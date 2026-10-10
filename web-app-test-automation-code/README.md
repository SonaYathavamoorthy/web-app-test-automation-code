# Web App Test Automation Suite

A QA project: a full test plan, 60 automated test cases and a bug log for a [30-day readmission risk app](https://github.com/SonaYathavamoorthy/readmission-risk-model-code) built with Streamlit and scikit-learn.

| Layer | Tool | Tests |
|-------|------|-------|
| Browser UI (end to end) | Playwright + pytest | 12 |
| Model behavior | pytest | 19 (8 checks, some parametrized) |
| SQL data validation | SQLite + pytest | 7 |
| API contract | Flask test client + pytest | 22 (9 checks, some parametrized) |
| Regression | GitHub Actions | every push |

## Results
**Expected results:** all non-defect tests pass, and 5 tests are marked as known defects (strict xfail). See [docs/BUG_REPORTS.md](docs/BUG_REPORTS.md).

Defects found include: gender alone moves risk by 18 points (traced to 2 positive cases in one group), a negative claim cost shows as invalid but still returns a score, and no upper bound on cost.

## Documents
- [Test plan](docs/TEST_PLAN.md) | [Test cases and traceability](docs/TEST_CASES.md) | [Bug reports](docs/BUG_REPORTS.md) | [Decisions](DECISIONS.md)

## Run it
```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -v
```
The UI tests start the Streamlit app themselves. Add `--runxfail` to see the known defects fail with their messages.
