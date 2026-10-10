# Bug Reports

Found while testing my own readmission app. Each has a strict-xfail test that will fail when the bug is fixed.

## BUG-001: Invalid negative claim cost is ignored silently, and a score is still shown
- **Severity:** Medium | **Test:** UI-10
- **Steps:** open the app, type -500 in "Total claim cost ($)", press Enter, click "Predict readmission risk".
- **Expected:** the field is flagged invalid and no score is shown until it is fixed.
- **Actual:** the field is flagged invalid, but a score of 12.1% appears. That is the score for the earlier value of 8000, not -500, so the screen shows one input and uses another.
- **Impact:** a user can read a score that does not match what they typed.
- **Suggested fix:** disable the button or show an error while any input is invalid.

## BUG-002: Gender alone moves the predicted risk by 18 points
- **Severity:** High (fairness) | **Tests:** M-06, D-07
- **Steps:** default inputs, Gender = Female gives 12.1%, change only Gender to Male gives 30.4%.
- **Expected:** no large change from one demographic field alone, or a documented reason.
- **Root cause found:** in the training table one gender group has 114 encounters and only 2 readmissions (1.8%), the other has 242 and 59 (24.4%). The model learned this small-sample gap. The model card does not mention it.
- **Impact:** the app would score otherwise identical patients very differently by gender.
- **Suggested fix:** drop gender as a feature or rebalance and re-evaluate, and add the limitation to the model card.

## BUG-003: Longer stays lower predicted risk for part of the range
- **Severity:** Low, needs clinical review | **Test:** M-07
- **Steps:** default inputs with length of stay 0, 3, 10, 30 days gives 16.0%, 12.1%, 7.7%, 6.5%.
- **Expected:** risk does not fall as stay length grows (assumption to confirm with a clinician).
- **Note:** the training data itself is mixed (stays over 7 days have a slightly lower rate than 3 to 7 days), so this is partly a data issue. Medication count is also non-monotonic. The model card already documents the same pattern for prior admissions.

## BUG-004: No upper limit or warning on claim cost
- **Severity:** Low | **Test:** UI-11
- **Steps:** enter 99,999,999,999 in claim cost, click Predict.
- **Expected:** rejected or warned as unrealistic.
- **Actual:** a normal-looking 25.8% score is returned.
- **Suggested fix:** set a maximum on the input (the API already limits it to 10,000,000).

## Observations (not logged as defects)
- The elevated-risk warning (50% or more) is reachable in only about 2% of a 73,500-point grid of allowed inputs, so most users will never see it.
- The app accepts clinically odd combinations, such as 0 active conditions with 20 medications.
- Running under scikit-learn 1.9.1 instead of the pinned 1.8.0 prints an InconsistentVersionWarning when the model loads.
