# Global Tuberculosis Dashboard

This is a Streamlit dashboard for exploring global tuberculosis burden, treatment-notification gaps, mortality, age and sex patterns, TB-HIV indicators, RR/MDR-TB burden, and simple trend projections.

The repository is trimmed for Streamlit deployment. It keeps only the application code, runtime dependencies, required processed dashboard data, and raw source files kept as reference.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at:

```text
http://localhost:8501
```

## Deploy on Streamlit Cloud

1. Push this project to GitHub.
2. In Streamlit Cloud, create a new app from the repository.
3. Set the app entry point to:

```text
app.py
```

4. Keep these deployment files in the repository root:

```text
app.py
requirements.txt
runtime.txt
```

`runtime.txt` pins the deployment to Python 3.11. This avoids compatibility issues with very new Python versions. `requirements.txt` also pins Plotly to `5.24.1`, which is a safer Streamlit Cloud version than `6.5.2`.

## Optional password protection

The app already includes an optional password screen. No code change is needed.

To enable password protection on Streamlit Cloud, open the app secrets and add:

```toml
APP_PASSWORD = "your-private-password"
```

If `APP_PASSWORD` is not set, the dashboard is public and opens without a password.

For local testing, you can either set an environment variable:

```bash
export APP_PASSWORD="your-private-password"
streamlit run app.py
```

or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the example password. Do not commit a real `.streamlit/secrets.toml` file.

## Project files

| File or folder | Purpose |
| --- | --- |
| `app.py` | Small Streamlit entrypoint. It configures the page, applies styles, runs the optional password gate, loads data, renders the sidebar, and calls each tab module. |
| `dashboard/config.py` | App paths, page settings, tab labels, and shared color constants. |
| `dashboard/styles.py` | Global CSS for the dashboard, including the rules that hide Streamlit toolbar/menu chrome. |
| `dashboard/auth.py` | Optional `APP_PASSWORD` password gate. |
| `dashboard/data.py` | Loads the four processed CSV files and returns the `DashboardData` object used by the app. |
| `dashboard/filters.py` | Sidebar controls and current filter state. |
| `dashboard/formatting.py` | Number, percent, rate, and percent-change helpers. |
| `dashboard/figures.py` | Shared Plotly styling helper. |
| `dashboard/layout.py` | Hero banner, current-scope caption, and footer. |
| `dashboard/tabs/` | One renderer module per dashboard tab. |
| `requirements.txt` | Runtime Python packages needed by Streamlit Cloud and local runs. |
| `runtime.txt` | Pins Streamlit Cloud to Python 3.11 for dependency stability. |
| `.streamlit/config.toml` | Streamlit configuration. |
| `.streamlit/secrets.toml.example` | Example secret file showing how to configure `APP_PASSWORD`. |
| `data/processed/tb_country_year.csv` | Required by the app. Main country-year dataset used for maps, rankings, comparisons, trends, TB-HIV, RR/MDR-TB, and projections. |
| `data/processed/tb_aggregates_year.csv` | Required by the app. Global and WHO-region aggregate metrics. |
| `data/processed/tb_age_sex_2024.csv` | Required by the app. Age and sex estimates used in the age/sex dashboard tab. |
| `data/processed/data_dictionary.csv` | Required by the app. Data dictionary displayed/downloaded from the dashboard. |
| `data/raw/` | Reference/source backup only. These files are kept for transparency, but the deployed Streamlit app does not read them. |

## Data folder note

`data/processed` is required because `app.py` reads these exact files:

```text
data/processed/tb_country_year.csv
data/processed/tb_aggregates_year.csv
data/processed/tb_age_sex_2024.csv
data/processed/data_dictionary.csv
```

`data/raw` is intentionally kept as reference, but it is not used by the deployed app.

## Code structure

The dashboard code is organized so `app.py` stays small and the implementation is easier to maintain:

```text
app.py
dashboard/
  auth.py
  config.py
  data.py
  figures.py
  filters.py
  formatting.py
  layout.py
  styles.py
  tabs/
    executive.py
    map.py
    trends.py
    age_sex.py
    tb_hiv_resistance.py
    forecast_data.py
```

Each tab receives the loaded dashboard data and the current sidebar selection state. This keeps the calculations and charts for each tab separate while preserving the same Streamlit app entrypoint for deployment.
