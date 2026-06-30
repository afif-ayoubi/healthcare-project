from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st

from dashboard.data import DashboardData


@dataclass(frozen=True)
class SelectionState:
    mode: str
    selection: str
    trend_range: tuple[int, int]
    map_year: int
    map_metric_label: str
    series: pd.DataFrame
    series_window: pd.DataFrame
    latest: Any
    latest_label: str


def geography_series(data: DashboardData, mode: str, selection: str) -> pd.DataFrame:
    if mode == "Global":
        out = data.aggregates[
            (data.aggregates["geo_level"] == "Global") & (data.aggregates["geography"] == "Global")
        ]
    elif mode == "WHO region":
        out = data.aggregates[
            (data.aggregates["geo_level"] == "WHO region") & (data.aggregates["geography"] == selection)
        ]
    else:
        out = data.country[data.country["country"] == selection]
    return out.sort_values("year").copy()


def filter_map_scope(frame: pd.DataFrame, mode: str, selection: str) -> pd.DataFrame:
    if mode == "WHO region":
        return frame[frame["g_whoregion"] == selection].copy()
    if mode == "Country":
        return frame[frame["country"] == selection].copy()
    return frame.copy()


def selected_age_data(data: DashboardData, mode: str, selection: str) -> pd.DataFrame:
    base = data.age_sex.copy()
    if mode == "WHO region":
        base = base[base["g_whoregion"] == selection]
    elif mode == "Country":
        base = base[base["country"] == selection]
    return base


def render_sidebar(data: DashboardData) -> SelectionState:
    with st.sidebar:
        st.markdown("### Dashboard controls")
        mode = st.radio("Analysis scope", ["Global", "WHO region", "Country"], horizontal=False)
        if mode == "WHO region":
            options = sorted(x for x in data.country["g_whoregion"].dropna().unique() if x != "Historical / Other")
            selection = st.selectbox(
                "WHO region",
                options,
                index=options.index("South-East Asia") if "South-East Asia" in options else 0,
            )
        elif mode == "Country":
            options = sorted(data.country["country"].dropna().unique())
            selection = st.selectbox("Country", options, index=options.index("Lebanon") if "Lebanon" in options else 0)
        else:
            selection = "Global"

        trend_range = st.slider("Trend window", data.min_year, data.latest_year, (2000, data.latest_year))
        map_year = st.slider("Snapshot year", data.min_year, data.latest_year, data.latest_year)
        map_metric_options = [
            "TB incidence rate per 100,000",
            "Estimated incident TB cases",
            "TB mortality rate per 100,000",
            "Diagnosis & treatment coverage (%)",
            "Estimated notification difference",
            "HIV-associated share of incident TB (%)",
            "Estimated RR/MDR-TB incidence",
        ]
        map_metric_label = st.selectbox("Map + ranking indicator", map_metric_options, index=0)
        st.markdown("---")
        st.markdown(
            "**Snapshot:** WHO-derived annual estimates and notifications, 2000–2024. "
            "Age-sex estimates are available for 2024 in this project package."
        )
        st.caption(
            "Analysis scope updates every eligible chart. Snapshot year updates snapshot charts. "
            "Trend window updates the time-series charts."
        )

    series = geography_series(data, mode, selection)
    series_window = series[series["year"].between(trend_range[0], trend_range[1])].copy()
    latest_rows = series[series["year"] <= map_year]
    latest = latest_rows.iloc[-1] if not latest_rows.empty else series.iloc[-1]
    return SelectionState(
        mode=mode,
        selection=selection,
        trend_range=trend_range,
        map_year=map_year,
        map_metric_label=map_metric_label,
        series=series,
        series_window=series_window,
        latest=latest,
        latest_label=f"{selection}, {int(latest['year'])}",
    )
