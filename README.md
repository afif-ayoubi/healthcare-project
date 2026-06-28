# Global Tuberculosis Burden and Treatment Gaps

A reproducible Streamlit dashboard for **MSBA382 – Healthcare Analytics**. The tool explores TB burden, notifications, diagnosis-and-treatment coverage, mortality, age/sex patterns, HIV-associated TB, and rifampicin/multidrug-resistant TB for 2000–2024.

## What the dashboard answers

- Where are estimated TB incidence and mortality highest?
- How have burden and case notifications changed over time?
- Which countries have the largest difference between estimated incident TB and notified new/relapse cases?
- How does the estimated 2024 burden vary by age and sex?
- Where are HIV-associated TB and RR/MDR-TB concentrated?
- What does a simple, clearly labelled exploratory trend projection show for a selected country?

## Important terminology

`notification_gap_num = estimated incident TB cases - notified new and relapse TB cases`

`calculated coverage (%) = notified new and relapse cases / estimated incident TB cases × 100`

The notification difference is a **surveillance and service-coverage signal**. It is not proof that every person in the difference was untreated. Estimated burden and notification counts have uncertainty, may refer to different reporting processes, and can be revised.

## Run locally

```bash
cd TB_Healthcare_Project
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Optional password screen

The dashboard runs without a password by default. To enable the protected landing page, either:

```bash
export APP_PASSWORD="your-private-password"
streamlit run app.py
```

or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the example value. Do not commit the real secrets file.

## Publish with Streamlit Community Cloud

1. Create a new GitHub repository and upload the contents of this folder.
2. In Streamlit Community Cloud, choose **Create app**.
3. Select the repository, branch, and `app.py` as the entry point.
4. Add `APP_PASSWORD` in **Advanced settings → Secrets** only when password protection is required.
5. Deploy, open every tab, test filters, and paste the public URL in the submission cover sheet/report.

**Published dashboard URL:** `[PASTE STREAMLIT URL HERE]`

Publishing requires the student's GitHub and Streamlit login; no account credentials are stored in this package.

## Rebuild and validate the data

The raw data files are included. Recreate the analytical tables and run validation with:

```bash
python scripts/prepare_data.py
python scripts/validate_data.py
python scripts/create_charts.py
```

Validation output is written to `outputs/data_validation.json`. The current package passes duplicate, year-range, non-negative burden, and age/sex availability checks.

## Data provenance

The project uses WHO Global Tuberculosis Programme indicators made available through public WHO-related repositories and mirrors. The package includes a source manifest with retrieval dates and SHA-256 hashes.

Primary references:

- World Health Organization. *Global tuberculosis report 2025*.
- World Health Organization. *Tuberculosis data* (downloadable CSVs and data dictionary).
- GTB-TME. *gtbreport2025* official GitHub repository.
- Open Numbers DDF mirror of WHO TB burden estimates, used because direct WHO CSV endpoints were not retrievable in the project runtime.
- A WHO-derived TidyTuesday snapshot, used only to map ISO3 codes to WHO region labels.

WHO states that annual time series are updated and the latest report supersedes earlier editions. Therefore, the reproducible country-level snapshot may differ slightly from rounded headline values in the published report.

## Project structure

```text
TB_Healthcare_Project/
├── app.py
├── requirements.txt
├── .streamlit/
├── data/
│   ├── raw/                # source snapshots, unchanged
│   └── processed/          # dashboard-ready files, dictionary and manifest
├── scripts/                # preparation, validation and chart generation
├── outputs/
│   ├── charts/
│   ├── screenshots/
│   └── data_validation.json
├── docs/                   # dashboard manual and project report
├── presentation/           # pitch deck, script and Q&A notes
└── tests/
```

## Analytical limitations

- Country-level estimates are ecological; they cannot establish individual-level risk or causation.
- WHO burden estimates have uncertainty intervals, although the mirror used here contains point estimates only.
- Coverage can occasionally exceed 100% because estimated burden and notified counts have uncertainty and are revised independently.
- The age/sex dataset is a 2024 cross-section in this package.
- Treatment cohort outcomes are not included; the dashboard focuses on diagnosis-and-treatment coverage and notification differences rather than individual treatment completion.
- The three-year projection is a linear extrapolation with a historical holdout error measure. It is not a WHO forecast and must not be used for clinical decisions.

## Citation

World Health Organization. (2025). *Global tuberculosis report 2025*. Geneva: WHO.
