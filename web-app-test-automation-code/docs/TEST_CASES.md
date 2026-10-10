# Test Cases

Automated test = function name in `tests/`. Result: P = pass, XF = expected failure (known defect).

## UI (tests/ui/test_app_ui.py)
| ID | Req | Steps | Expected | Result |
|----|----|-------|----------|--------|
| UI-01 | R1 | Open the app | Title and not-a-clinical-tool disclaimer visible | P |
| UI-02 | R1 | Read the sidebar | Model name, AUC and positive rate equal `metrics.json` | P |
| UI-03 | R3 | Click Predict with default inputs | Score equals model output (within 0.1% display rounding) | P |
| UI-04 | R2 | Open the app, do not click | No score shown | P |
| UI-05 | R3 | Set length of stay 10 and cost 50000, Predict | Score equals model output | P |
| UI-06 | R3 | Choose Male, Predict | Score equals model output for gender=1 | P |
| UI-07 | R4 | Default inputs, Predict | "Lower predicted risk" message | P |
| UI-08 | R4 | Set age 70, stay 15, prior 1, conditions 0, meds 20, male, cost 150000 | Score at least 50% and "Elevated risk" warning | P |
| UI-09 | R5 | Enter -500 in cost | Field marked invalid | P |
| UI-10 | R5 | Enter -500, click Predict | No score is produced for an invalid input | XF (BUG-001) |
| UI-11 | R5 | Enter 99,999,999,999, click Predict | Rejected or warned | XF (BUG-004) |
| UI-12 | R3 | Click Predict four times | Same score each time, no error banner | P |

## Model (tests/model/test_model_behavior.py)
| ID | Req | Check | Result |
|----|----|-------|--------|
| M-01 | R6 | Feature order and count match training metadata | P |
| M-02 | R6 | Probability between 0 and 1 for 6 age and cost combinations | P |
| M-03 | R6 | Same input gives same output | P |
| M-04 | R6 | All-minimum and all-maximum inputs do not crash | P |
| M-05 | R1 | Reported AUC is between 0.7 and 1.0 | P |
| M-06 | R6 | Changing only gender moves risk by 10 points or less | XF (BUG-002) |
| M-07 | R6 | Longer stay does not reduce predicted risk | XF (BUG-003) |
| M-08 | R6 | Prior-admissions effect matches the documented limitation in the model card | P |

## Data (tests/data/test_features_sql.py)
| ID | Req | SQL check | Result |
|----|----|-----------|--------|
| D-01 | R7 | `COUNT(*)` is 356 | P |
| D-02 | R7 | `COUNT(*) - COUNT(DISTINCT encounter_id)` is 0 | P |
| D-03 | R7 | No NULLs in any model column | P |
| D-04 | R7 | Age, stay and cost inside the ranges the app accepts | P |
| D-05 | R7 | Label is 0 or 1 and positive rate is 15% to 19% | P |
| D-06 | R7 | Gender is 0 or 1 | P |
| D-07 | R7 | Each gender group has at least 10 positive cases | XF (BUG-002 cause) |

## API (tests/api/test_api.py)
| ID | Req | Check | Result |
|----|----|-------|--------|
| A-01 | R8 | `GET /health` returns 200 and status ok | P |
| A-02 | R8 | Valid `POST /predict` returns 200 with `risk` and `flagged` only | P |
| A-03 | R8 | API risk equals direct model output | P |
| A-04 | R8 | Each of 7 missing fields returns 422 and names the field | P (7) |
| A-05 | R8 | 5 out-of-range values return 422 | P (5) |
| A-06 | R8 | String, null, boolean and list values return 422 | P (4) |
| A-07 | R8 | Non-JSON body returns 400 | P |
| A-08 | R8 | `GET /predict` returns 405 | P |
| A-09 | R8 | Unknown route returns 404 | P |

## Traceability
R1: UI-01, UI-02, M-05 | R2: UI-04 | R3: UI-03, 05, 06, 12, A-03 | R4: UI-07, UI-08 | R5: UI-09, 10, 11 | R6: M-01 to M-08 | R7: D-01 to D-07 | R8: A-01 to A-09
