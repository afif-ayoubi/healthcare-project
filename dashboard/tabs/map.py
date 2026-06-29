from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState, filter_map_scope


def render_map_tab(data: DashboardData, state: SelectionState) -> None:
    st.subheader(f"Geographic pattern — {state.map_year}")
    metric_options = {
        "TB incidence rate per 100,000": ("e_inc_100k", "Incidence /100k", "YlOrRd"),
        "Estimated incident TB cases": ("e_inc_num", "Estimated cases", "YlOrRd"),
        "TB mortality rate per 100,000": ("e_mort_100k", "Mortality /100k", "OrRd"),
        "Diagnosis & treatment coverage (%)": ("c_cdr", "Coverage %", "Teal"),
        "Estimated notification difference": ("notification_gap_num_nonnegative", "Notification difference", "Reds"),
        "HIV-associated share of incident TB (%)": ("hiv_incidence_share_pct", "HIV-associated share %", "Purples"),
        "Estimated RR/MDR-TB incidence": ("e_inc_rr_num", "RR/MDR-TB cases", "Magenta"),
    }
    map_label = st.selectbox("Map indicator", list(metric_options), index=0)
    metric, display_label, scale = metric_options[map_label]
    map_data = data.country[data.country["year"] == state.map_year].dropna(subset=["iso3", metric]).copy()
    scoped = filter_map_scope(map_data, state.mode, state.selection)

    fig = px.choropleth(
        map_data,
        locations="iso3",
        color=metric,
        hover_name="country",
        hover_data={
            "iso3": False,
            "g_whoregion": True,
            "e_inc_num": ":,.0f",
            "e_inc_100k": ":.1f",
            "c_cdr": ":.1f",
            "notification_gap_num_nonnegative": ":,.0f",
        },
        color_continuous_scale=scale,
        title=map_label,
        labels={metric: display_label, "g_whoregion": "WHO region"},
    )
    fig.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#C9D6DC", projection_type="natural earth")
    fig.update_layout(coloraxis_colorbar=dict(title=display_label))
    st.plotly_chart(style_figure(fig, 550), use_container_width=True)

    if state.mode != "Global":
        st.caption(f"The map remains global for context; the ranking below is filtered to **{state.selection}**.")
    rank = scoped.nlargest(15, metric)[["country", "g_whoregion", metric, "e_inc_num", "c_cdr"]].copy()
    rank = rank.rename(columns={"country": "Country", "g_whoregion": "WHO region", metric: display_label, "e_inc_num": "Estimated TB cases", "c_cdr": "Coverage %"})
    left, right = st.columns([1.2, 1])
    with left:
        bar = rank.sort_values(display_label)
        fig = px.bar(
            bar,
            x=display_label,
            y="Country",
            orientation="h",
            color=display_label,
            color_continuous_scale=scale,
            title=f"Top countries by {display_label.lower()}",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)
    with right:
        st.dataframe(
            rank.style.format({display_label: "{:,.1f}", "Estimated TB cases": "{:,.0f}", "Coverage %": "{:,.1f}"}),
            use_container_width=True,
            hide_index=True,
            height=500,
        )
