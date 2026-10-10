# Test Plan: 30-Day Readmission Risk Predictor

## 1. Scope
**System under test (SUT):** the Streamlit app, the trained model, its training table, and a small JSON prediction API (`/health`, `/predict`) in `sut/`. The model and app are from my own project, [readmission-risk-model-code](https://github.com/SonaYathavamoorthy/readmission-risk-model-code); the API was added here so the model could be tested at the service level.

**In scope:** page load and content, input handling, prediction correctness, risk messaging, model behavior, training-data integrity, API contract and validation.
**Out of scope:** clinical validity (the data is synthetic), performance and load testing, cross-browser testing beyond Chromium, security testing.

## 2. Requirements under test
| ID | Requirement (from the app, README and model card) |
|----|-----|
| R1 | The app shows the title, a disclaimer that it is not a clinical tool, and the model's reported AUC and positive rate |
| R2 | A score is only produced after the user clicks Predict |
| R3 | The displayed score equals the model's output for the entered inputs |
| R4 | Scores of 50% or more show an elevated-risk warning; lower scores show a success message |
| R5 | Inputs are limited to the stated ranges (cost cannot be negative) |
| R6 | The model returns a valid probability for every allowed input and is deterministic |
| R7 | The training table is complete, unique, in range, and matches the documented 356 rows and about 17% readmission rate |
| R8 | The API returns correct status codes and clear errors for bad requests |

## 3. Approach
| Layer | Tool | What it checks |
|-------|------|----------------|
| UI (end to end) | Playwright + pytest, real browser against a live Streamlit server | R1 to R5 |
| Model behavior | pytest with the model called directly as an oracle | R3, R6, plus expected-direction checks |
| Data validation | SQL queries on the training table loaded into SQLite | R7 |
| API | pytest with the Flask test client | R8 |
| Regression | GitHub Actions runs every test on each push | all |

**Oracle approach:** UI and API results are compared against the model called directly, so a test fails if the UI or API changes the answer.

**Known-defect handling:** a test for a confirmed defect is marked `xfail(strict=True)` with the bug ID. The suite stays green, the defect stays documented, and the test fails loudly the day the bug is fixed so the marker gets removed.

## 4. Entry and exit criteria
- **Entry:** app starts and `/_stcore/health` returns ok.
- **Exit:** all non-defect tests pass; every failing expectation is logged as a bug with severity.

## 5. Risks and assumptions
- The model is trained on 356 synthetic encounters, so some "unexpected" behavior comes from data size, not code (see BUG-002).
- The model was saved with scikit-learn 1.8.0. Running under another version prints a warning, so `requirements.txt` pins it.
- Expected-direction checks (for example "longer stay should not lower risk") are clinical assumptions. They need review by someone with clinical knowledge before being treated as certain defects.
