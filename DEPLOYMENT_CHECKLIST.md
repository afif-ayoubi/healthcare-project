# Deployment and submission checklist

## Personalize before publishing

- Replace `[Student Name]` in the manual, report, pitch deck and script.
- Confirm the programme/department labels on each cover page.
- Choose whether the dashboard needs password protection. When required, add `APP_PASSWORD` to Streamlit Secrets; never commit a real password.

## Publish the dashboard

- Create a GitHub repository and upload the project files.
- Deploy `app.py` through Streamlit Community Cloud.
- Open all six tabs and test Global, WHO region and Country filters.
- Test the CSV download and at least one country forecast.
- Copy the final URL into:
  - `README.md`
  - the final slide of `TB_Healthcare_Analytics_Pitch.pptx`
  - `TB_Individual_Project_Report.docx`
  - the Moodle submission notes, if requested.

**Published URL:** `[PASTE STREAMLIT URL HERE]`

## Final quality check

- Run `python scripts/validate_data.py` and confirm `status: PASS`.
- Run `pytest -q` and confirm all tests pass.
- Confirm the manual is 4–5 pages.
- Rehearse the pitch with a strict five-minute timer.
- Upload the dashboard package by 30 June 2026, prepare for the 1 July presentation, and submit the report by 5 July 2026.
