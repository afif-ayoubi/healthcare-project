from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.config import CORAL, GOLD, NAVY, TEAL
from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState, filter_map_scope, selected_age_data
from dashboard.formatting import fmt_count, fmt_pct, fmt_rate


MAP_METRIC_OPTIONS = {
    "TB incidence rate per 100,000": ("e_inc_100k", "Incidence /100k", "YlOrRd"),
    "Estimated incident TB cases": ("e_inc_num", "Estimated cases", "YlOrRd"),
    "TB mortality rate per 100,000": ("e_mort_100k", "Mortality /100k", "OrRd"),
    "Diagnosis & treatment coverage (%)": ("c_cdr", "Coverage %", "Teal"),
    "Estimated notification difference": ("notification_gap_num_nonnegative", "Notification difference", "Reds"),
    "HIV-associated share of incident TB (%)": ("hiv_incidence_share_pct", "HIV-associated share %", "Purples"),
    "Estimated RR/MDR-TB incidence": ("e_inc_rr_num", "RR/MDR-TB cases", "Magenta"),
}


def render_one_page_dashboard(data: DashboardData, state: SelectionState) -> None:
    """Render the coordinated one-page dashboard surface."""
    _render_kpis(state)
    _render_filter_guide()

    _render_section_header(
        "Trend over time",
        "Uses Analysis scope + Trend window. Snapshot year appears as a dotted marker when it falls inside the trend window.",
    )
    top_left, top_right = st.columns([1.08, 1])
    with top_left:
        _render_burden_trend(state)
    with top_right:
        _render_rate_trend(state)

    _render_section_header(
        "Snapshot map and ranking",
        "Uses Analysis scope + Snapshot year + Map/ranking indicator. The map stays global for context; the ranking is scoped.",
    )
    _render_map(data, state)

    _render_section_header(
        "Regional comparison",
        "Uses Snapshot year and shows all WHO regions for context.",
    )
    _render_region_scatter(data, state)

    _render_section_header(
        "Demographics and special burden",
        "Age-sex uses Analysis scope only because it is a fixed 2024 snapshot. TB-HIV/RR/MDR uses Analysis scope + Snapshot year.",
    )
    demo_col, special_col = st.columns([1, 1])
    with demo_col:
        _render_age_sex(data, state)
    with special_col:
        _render_tb_hiv_resistance(data, state)

    with st.expander("Brief data notes"):
        st.markdown(
            """
            WHO burden values are estimates and can be revised across releases. The notification difference is estimated
            incident TB minus notified new and relapse cases; it is a surveillance and service-coverage signal, not a
            patient-level untreated count. Age-sex estimates in this project are available as a 2024 cross-section.
            """
        )


def _render_filter_guide() -> None:
    st.markdown(
        """
        <div class="filter-guide">
          <span class="filter-chip">Scope: most charts</span>
          <span class="filter-chip">Trend window: time-series only</span>
          <span class="filter-chip">Snapshot year: snapshot charts</span>
          <span class="filter-chip">Indicator: map + ranking only</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section_header(title: str, note: str) -> None:
    st.markdown(
        f'<div class="section-head"><h3>{title}</h3><p>{note}</p></div>',
        unsafe_allow_html=True,
    )


def _render_kpis(state: SelectionState) -> None:
    latest = state.latest
    st.markdown(f"### Coordinated analytical snapshot — {state.latest_label}")
    cols = st.columns(5)
    cols[0].metric("Estimated incident cases", fmt_count(latest.get("e_inc_num")))
    cols[1].metric("Incidence /100k", fmt_rate(latest.get("e_inc_100k")))
    cols[2].metric("Estimated TB deaths", fmt_count(latest.get("e_mort_num")))
    cols[3].metric("Treatment coverage", fmt_pct(latest.get("c_cdr")))
    cols[4].metric("Notification difference", fmt_count(latest.get("notification_gap_num_nonnegative")))


def _render_burden_trend(state: SelectionState) -> None:
    burden = state.series_window[["year", "e_inc_num", "c_newinc"]].melt(
        "year", var_name="measure", value_name="people"
    )
    burden["measure"] = burden["measure"].map(
        {
            "e_inc_num": "Estimated incident TB",
            "c_newinc": "Notified new & relapse",
        }
    )
    fig = px.line(
        burden,
        x="year",
        y="people",
        color="measure",
        markers=True,
        color_discrete_map={"Estimated incident TB": CORAL, "Notified new & relapse": TEAL},
        title="Estimated burden vs notifications",
    )
    _add_snapshot_marker(fig, state)
    fig.update_yaxes(tickformat="~s", title="People")
    fig.update_xaxes(title="")
    st.plotly_chart(style_figure(fig, 390), use_container_width=True)
    st.caption(f"{state.selection} · {state.trend_range[0]}-{state.trend_range[1]} · dotted line = snapshot {state.map_year}")


def _render_rate_trend(state: SelectionState) -> None:
    rates = state.series_window[["year", "e_inc_100k", "e_mort_100k"]].melt(
        "year", var_name="measure", value_name="rate"
    )
    rates["measure"] = rates["measure"].map(
        {
            "e_inc_100k": "Incidence rate",
            "e_mort_100k": "Mortality rate",
        }
    )
    fig = px.line(
        rates,
        x="year",
        y="rate",
        color="measure",
        markers=True,
        color_discrete_map={"Incidence rate": NAVY, "Mortality rate": GOLD},
        title="Incidence and mortality rates",
    )
    _add_snapshot_marker(fig, state)
    fig.update_yaxes(title="Per 100,000")
    fig.update_xaxes(title="")
    st.plotly_chart(style_figure(fig, 390), use_container_width=True)
    st.caption(f"{state.selection} · {state.trend_range[0]}-{state.trend_range[1]} · dotted line = snapshot {state.map_year}")


def _render_map(data: DashboardData, state: SelectionState) -> None:
    metric, display_label, scale = MAP_METRIC_OPTIONS[state.map_metric_label]
    map_data = data.country[data.country["year"] == state.map_year].dropna(subset=["iso3", metric]).copy()
    scoped = filter_map_scope(map_data, state.mode, state.selection)

    map_col, rank_col = st.columns([1.25, 1])
    with map_col:
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
            title=state.map_metric_label,
            labels={metric: display_label, "g_whoregion": "WHO region"},
        )
        fig.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#C9D6DC", projection_type="natural earth")
        fig.update_layout(coloraxis_colorbar=dict(title=display_label))
        st.plotly_chart(style_figure(fig, 460), use_container_width=True)
        st.caption(f"Global context · snapshot {state.map_year} · indicator controls this map and the ranking.")

    with rank_col:
        if scoped.empty:
            st.info("No country records are available for the selected map scope.")
            return

        rank = scoped.nlargest(10, metric).sort_values(metric)
        bar = px.bar(
            rank,
            x=metric,
            y="country",
            orientation="h",
            color=metric,
            color_continuous_scale=scale,
            title=f"Highest countries by {display_label.lower()}",
            labels={metric: display_label, "country": ""},
            hover_data={"g_whoregion": True, "e_inc_num": ":,.0f", "c_cdr": ":.1f"},
        )
        bar.update_layout(coloraxis_showscale=False)
        if metric.endswith("num") or metric == "notification_gap_num_nonnegative":
            bar.update_xaxes(tickformat="~s")
        st.plotly_chart(style_figure(bar, 460), use_container_width=True)
        st.caption(f"{state.selection} · snapshot {state.map_year} · same indicator as map")


def _render_region_scatter(data: DashboardData, state: SelectionState) -> None:
    region_snapshot = data.aggregates[
        (data.aggregates["geo_level"] == "WHO region") & (data.aggregates["year"] == state.map_year)
    ].dropna(subset=["e_inc_100k", "c_cdr", "e_inc_num"])
    fig = px.scatter(
        region_snapshot,
        x="e_inc_100k",
        y="c_cdr",
        size="e_inc_num",
        color="geography",
        text="geography",
        hover_data={"e_inc_num": ":,.0f", "notification_gap_num_nonnegative": ":,.0f"},
        title="WHO regions: burden and coverage",
        labels={
            "e_inc_100k": "Incidence /100k",
            "c_cdr": "Coverage %",
            "geography": "WHO region",
            "e_inc_num": "Estimated cases",
        },
        size_max=62,
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(style_figure(fig, 460), use_container_width=True)
    st.caption(f"All WHO regions · snapshot {state.map_year}")


def _render_age_sex(data: DashboardData, state: SelectionState) -> None:
    non_overlapping = ["0_4", "5_9", "10_14", "15_19", "20_24", "25_34", "35_44", "45_54", "55_64", "65plus"]
    age_scope = selected_age_data(data, state.mode, state.selection)
    age_scope = age_scope[age_scope["age_group"].isin(non_overlapping) & age_scope["sex"].isin(["m", "f"])].copy()
    if age_scope.empty:
        st.warning("No age-sex estimate is available for the selected geography.")
        return

    age_order = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    age_summary = age_scope.groupby(["age_group_label", "sex_label"], as_index=False)["e_inc_num"].sum(min_count=1)
    age_summary["age_group_label"] = pd.Categorical(age_summary["age_group_label"], categories=age_order, ordered=True)
    age_summary = age_summary.sort_values("age_group_label")

    totals = age_scope.groupby("sex_label")["e_inc_num"].sum(min_count=1)
    male = float(totals.get("Male", np.nan))
    female = float(totals.get("Female", np.nan))
    ratio = male / female if female and not np.isnan(female) else np.nan
    st.caption(
        f"2024 age-sex snapshot for {state.selection} · male:female ratio "
        f"{'N/A' if np.isnan(ratio) else f'{ratio:.2f}'}"
    )

    fig = px.bar(
        age_summary,
        x="age_group_label",
        y="e_inc_num",
        color="sex_label",
        barmode="group",
        color_discrete_map={"Male": TEAL, "Female": CORAL},
        title="Age-sex distribution",
        labels={"age_group_label": "Age group", "e_inc_num": "Estimated cases", "sex_label": "Sex"},
    )
    fig.update_yaxes(tickformat="~s")
    st.plotly_chart(style_figure(fig, 390), use_container_width=True)


def _render_tb_hiv_resistance(data: DashboardData, state: SelectionState) -> None:
    current = data.country[data.country["year"] == state.map_year].copy()
    scoped = filter_map_scope(current, state.mode, state.selection)
    if scoped.empty:
        st.info("No TB-HIV or RR/MDR-TB records are available for the selected scope.")
        return

    hiv_top = scoped.dropna(subset=["e_inc_tbhiv_num"]).nlargest(8, "e_inc_tbhiv_num")
    rr_top = scoped.dropna(subset=["e_inc_rr_num"]).nlargest(8, "e_inc_rr_num")
    special = pd.concat(
        [
            hiv_top.assign(indicator="HIV-associated TB", value=hiv_top["e_inc_tbhiv_num"]),
            rr_top.assign(indicator="RR/MDR-TB", value=rr_top["e_inc_rr_num"]),
        ],
        ignore_index=True,
    )
    if special.empty:
        st.info("No TB-HIV or RR/MDR-TB values are available for this selection.")
        return

    fig = px.bar(
        special.sort_values("value"),
        x="value",
        y="country",
        color="indicator",
        orientation="h",
        barmode="group",
        color_discrete_map={"HIV-associated TB": CORAL, "RR/MDR-TB": TEAL},
        title="TB-HIV and RR/MDR-TB burden",
        labels={"value": "Estimated cases", "country": "", "indicator": ""},
        hover_data={"g_whoregion": True},
    )
    fig.update_xaxes(tickformat="~s")
    st.plotly_chart(style_figure(fig, 390), use_container_width=True)
    st.caption(f"{state.selection} · snapshot {state.map_year}")


def _add_snapshot_marker(fig, state: SelectionState) -> None:
    start, end = state.trend_range
    if start <= state.map_year <= end:
        fig.add_vline(
            x=state.map_year,
            line_width=2,
            line_dash="dot",
            line_color="#64748B",
            annotation_text=f"Snapshot {state.map_year}",
            annotation_position="top right",
        )
