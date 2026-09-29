# Capstone Requirement Mapping

This repository implements the three broad capstone stages discussed for the **PharmEasy Regional Order Pulse** project.

## 1. Define and plan a real-world AI-powered application
- Business context: compare regional order, sales, and profit performance.
- Decision-support objective: surface material month-on-month sales movements for human review.
- Data note: all included records are synthetic demonstration data, not actual PharmEasy data.

## 2. Build a functional prototype
- Python cleaning and validation: `pipeline.py`
- SQLite persistence and SQL metrics: `data/pharmeasy.db` (recreated by the pipeline)
- Month-on-month movement flags: `outputs/risk_flags.csv` (strictly greater than 8% absolute change)
- State persistence and audit trail: `outputs/state.json`, `outputs/audit_log.json`
- Decision-support reports: `outputs/cii_report.md`, `outputs/business_memo.md`
- Interactive dashboard: `app.py` (Streamlit + Plotly)

## 3. Present a professional portfolio artifact
- Project overview and run instructions: `README.md`
- Outputs and reproducible source code are included in the repository.
- Tests: `python -m unittest discover -s tests -v`

## Reproducibility
Run `python run_all.py` from this directory, then `streamlit run app.py`.
