from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState


def render_trends_tab(data: DashboardData, state: SelectionState) -> None:
    st.subheader("Country and regional comparisons")
    metric_labels = {
        "Incidence rate per 100,000": "e_inc_100k",
        "Mortality rate per 100,000": "e_mort_100k",
        "Estimated incident cases": "e_inc_num",
        "Notified new & relapse cases": "c_newinc",
        "Diagnosis & treatment coverage (%)": "c_cdr",
        "Estimated notification difference": "notification_gap_num_nonnegative",
        "HIV-associated incident TB": "e_inc_tbhiv_num",
        "Estimated RR/MDR-TB incidence": "e_inc_rr_num",
    }
    trend_label = st.selectbox("Trend indicator", list(metric_labels), index=0)
    trend_metric = metric_labels[trend_label]
    all_countries = sorted(data.country["country"].dropna().unique())
    if state.mode == "Country":
        default_countries = [state.selection]
    else:
        default_countries = [x for x in ["India", "Indonesia", "Philippines", "China", "Pakistan"] if x in all_countries]
    compare = st.multiselect("Countries to compare (up to 8)", all_countries, default=default_countries, max_selections=8)
    if not compare:
        st.info("Select at least one country.")
    else:
        comp = data.country[data.country["country"].isin(compare) & data.country["year"].between(*state.trend_range)].copy()
        fig = px.line(
            comp,
            x="year",
            y=trend_metric,
            color="country",
            markers=True,
            title=trend_label,
            labels={trend_metric: trend_label, "year": "Year", "country": "Country"},
        )
        if trend_metric.endswith("num") or trend_metric in {"c_newinc", "notification_gap_num_nonnegative"}:
            fig.update_yaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)

        summary_rows = []
        for name, grp in comp.groupby("country"):
            s = grp.set_index("year")[trend_metric].dropna()
            start_available = int(s.index.min()) if not s.empty else None
            end_available = int(s.index.max()) if not s.empty else None
            change = (s.iloc[-1] / s.iloc[0] - 1) * 100 if len(s) >= 2 and s.iloc[0] != 0 else np.nan
            summary_rows.append({
                "Country": name,
                "First year": start_available,
                "Latest year": end_available,
                "First value": s.iloc[0] if not s.empty else np.nan,
                "Latest value": s.iloc[-1] if not s.empty else np.nan,
                "Change %": change,
            })
        change_df = pd.DataFrame(summary_rows).sort_values("Latest value", ascending=False)
        st.dataframe(
            change_df.style.format({"First value": "{:,.1f}", "Latest value": "{:,.1f}", "Change %": "{:+,.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### WHO region comparison")
    region_snapshot = data.aggregates[
        (data.aggregates["geo_level"] == "WHO region") & (data.aggregates["year"] == state.map_year)
    ].copy()
    region_snapshot = region_snapshot.sort_values("e_inc_num", ascending=False)
    fig = px.scatter(
        region_snapshot,
        x="e_inc_100k",
        y="c_cdr",
        size="e_inc_num",
        color="geography",
        text="geography",
        hover_data={"e_inc_num": ":,.0f", "notification_gap_num_nonnegative": ":,.0f"},
        title="Burden and service coverage by WHO region",
        labels={"e_inc_100k": "Incidence per 100,000", "c_cdr": "Coverage (%)", "geography": "WHO region", "e_inc_num": "Estimated cases"},
        size_max=70,
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(style_figure(fig, 500), use_container_width=True)
