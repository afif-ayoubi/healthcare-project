from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from dashboard.config import DATA_DIR


@dataclass(frozen=True)
class DashboardData:
    country: pd.DataFrame
    aggregates: pd.DataFrame
    age_sex: pd.DataFrame
    data_dictionary: pd.DataFrame
    min_year: int
    latest_year: int


@st.cache_data(show_spinner=False)
def load_data() -> DashboardData:
    country = pd.read_csv(DATA_DIR / "tb_country_year.csv")
    aggregates = pd.read_csv(DATA_DIR / "tb_aggregates_year.csv")
    age_sex = pd.read_csv(DATA_DIR / "tb_age_sex_2024.csv")
    dictionary = pd.read_csv(DATA_DIR / "data_dictionary.csv")
    for frame in (country, aggregates, age_sex):
        frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    return DashboardData(
        country=country,
        aggregates=aggregates,
        age_sex=age_sex,
        data_dictionary=dictionary,
        min_year=int(country["year"].min()),
        latest_year=int(country["year"].max()),
    )
