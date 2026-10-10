Healthcare Quality Measures and Cost Analytics

SQL and Python analytics that compute HEDIS-style quality measures and cost and utilization metrics from an EHR star-schema warehouse, the way a health plan or hospital quality team does.

These are simplified, HEDIS-style measures on synthetic data. They are not NCQA-certified, and the numbers describe a simulated population, not real patients. HEDIS is a registered trademark of NCQA.

Business question

Quality teams are asked three things every year: are we giving recommended care, what does care cost, and where is the money concentrated? This project answers them from patient-level data.

Key findings (measurement year 2025)
Cost is concentrated. The top 5% of members account for 47.0% of total cost, and the top 10% for 64.6%.
Average cost is $15,217 per member-year across 450 members (446.9 member-years, $6.8M total).
Utilization: 185.7 ER visits and 49.2 inpatient admissions per 1,000 member-years.
Chronic conditions drive cost. Cost per member-year is $28,113 for diabetes only, $20,675 for diabetes plus hypertension, $18,299 for hypertension only, and $13,851 for neither. Some groups are small, so read the ordering, not the exact dollars.
Blood pressure control is 75.3% (58 of 77), colorectal screening is 51.5% (85 of 165), and 30-day readmission is 23.8% (5 of 21).
Quality measures
Measure	Denominator	Numerator	Result
Controlling high blood pressure	Age 18-85, alive at year end, hypertension diagnosed by 30 Jun	Most recent BP in the year below 140/90 (no reading counts as not controlled)	75.3% (58 of 77)
Colorectal cancer screening	Age 45-75, alive at year end	Colonoscopy in the last 10 years, or stool test in the year	51.5% (85 of 165)
30-day all-cause readmission (lower is better)	Inpatient discharges in the year	Followed by another inpatient stay within 30 days	23.8% (5 of 21)
Diabetes: HbA1c tested / poor control	Age 18-75, type 2 diabetes	Tested in year / latest above 9%	100% / 0% (not informative)

Simplifications: no continuous-enrollment rule, no exclusions beyond age and vital status, diagnoses from the problem list rather than claims, and patients (not member-months) as the unit. Each rule is a small, separately tested function in src/measures.py.

Why two diabetes measures are flagged: every simulated diabetic's latest HbA1c is between 2.4 and 6.9, so the data shows no care gaps. I kept the measures to show the logic and tests, marked them informative = False, and left them off the chart.

Data and pipeline
Synthea synthetic patients (Virginia), generated with fixed seeds so results are reproducible: 494 patients, 28,602 encounters, 411,931 observations, about 10 years of history.
ETL into a star schema, reused from my Synthetic EHR Patient Journey Pipeline.
Measures computed in SQL and Python, with 10 unit tests and GitHub Actions CI.
Output CSV extracts in tableau_data/ for a Tableau Public dashboard (build steps in tableau/TABLEAU_GUIDE.md).
Limitations
Synthetic data, so no real-world validity claims.
Small denominators (for example 21 inpatient stays) make single rates noisy.
The colorectal measure is understated because only about 10 years of history exist.
Mammography is too sparse to build a breast-cancer-screening measure.
Run it
bash
pip install -r requirements.txt
bash src/generate_data.sh 450 2026      # needs Java 11+
python -m src.etl.run_pipeline          # build the warehouse
python src/measures.py                  # compute measures, write tableau_data/ and docs/
pytest tests/ -v

Tech: Python, pandas, SQL, SQLite, matplotlib, pytest, GitHub Actions. Design choices are in DECISIONS.md.

