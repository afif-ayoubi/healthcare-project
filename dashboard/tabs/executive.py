from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.config import CORAL, GOLD, NAVY, TEAL
from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState
from dashboard.formatting import fmt_count, fmt_pct, fmt_rate, pct_change


def render_executive_tab(data: DashboardData, state: SelectionState) -> None:
    latest = state.latest
    st.subheader(f"Executive snapshot — {state.latest_label}")
    cols = st.columns(5)
    cols[0].metric("Estimated incident cases", fmt_count(latest.get("e_inc_num")))
    cols[1].metric("Incidence per 100,000", fmt_rate(latest.get("e_inc_100k")))
    cols[2].metric("Estimated TB deaths", fmt_count(latest.get("e_mort_num")))
    cols[3].metric("Diagnosis & treatment coverage", fmt_pct(latest.get("c_cdr")))
    cols[4].metric("Estimated notification difference", fmt_count(latest.get("notification_gap_num_nonnegative")))

    st.markdown(
        '<div class="warning-note"><b>Interpretation:</b> the notification difference equals estimated incident cases minus notified new and relapse cases. '
        'It is a surveillance and service-coverage signal, not proof that every person in the difference was untreated. WHO burden values are estimates and carry uncertainty.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    left, right = st.columns([1.15, 1])
    with left:
        burden = state.series_window[["year", "e_inc_num", "c_newinc"]].melt(
            "year", var_name="measure", value_name="people"
        )
        burden["measure"] = burden["measure"].map({
            "e_inc_num": "Estimated incident TB",
            "c_newinc": "Notified new & relapse",
        })
        fig = px.line(
            burden,
            x="year",
            y="people",
            color="measure",
            markers=True,
            color_discrete_map={"Estimated incident TB": CORAL, "Notified new & relapse": TEAL},
            title="Estimated burden versus notified cases",
        )
        fig.update_yaxes(tickformat="~s", title="People")
        fig.update_xaxes(title="")
        st.plotly_chart(style_figure(fig), use_container_width=True)
    with right:
        rates = state.series_window[["year", "e_inc_100k", "e_mort_100k"]].melt(
            "year", var_name="measure", value_name="rate"
        )
        rates["measure"] = rates["measure"].map({
            "e_inc_100k": "Incidence rate",
            "e_mort_100k": "Mortality rate",
        })
        fig = px.line(
            rates,
            x="year",
            y="rate",
            color="measure",
            markers=True,
            color_discrete_map={"Incidence rate": NAVY, "Mortality rate": GOLD},
            title="TB incidence and mortality rates",
        )
        fig.update_yaxes(title="Per 100,000")
        fig.update_xaxes(title="")
        st.plotly_chart(style_figure(fig), use_container_width=True)

    start, end = state.trend_range
    indexed = state.series.set_index("year")
    incidence_change = pct_change(indexed["e_inc_100k"], start, end)
    mortality_change = pct_change(indexed["e_mort_100k"], start, end)
    coverage_change = pct_change(indexed["c_cdr"], start, end)
    notif_change = pct_change(indexed["c_newinc"], start, end)

    st.markdown("### Decision-oriented interpretation")
    insight_cols = st.columns(3)
    insight_cols[0].markdown(
        f'<div class="insight"><b>Burden direction</b><br>Incidence changed by <strong>{fmt_pct(incidence_change)}</strong> and mortality by '
        f'<strong>{fmt_pct(mortality_change)}</strong> between {start} and {end}. Negative values indicate improvement.</div>',
        unsafe_allow_html=True,
    )
    insight_cols[1].markdown(
        f'<div class="insight"><b>Service reach</b><br>Notifications changed by <strong>{fmt_pct(notif_change)}</strong>, while calculated coverage changed by '
        f'<strong>{fmt_pct(coverage_change)}</strong>. Interpret this alongside estimated burden, not in isolation.</div>',
        unsafe_allow_html=True,
    )
    pandemic_note = "The 2020 notification fall is visible in the global series and is consistent with pandemic-related service disruption." if state.mode == "Global" else "Use the time series to check whether 2020 interrupted detection and reporting in this geography."
    insight_cols[2].markdown(
        f'<div class="insight"><b>System resilience</b><br>{pandemic_note}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Countries contributing most to the 2024 analytical snapshot")
    snapshot = data.country[data.country["year"] == state.map_year].dropna(subset=["country", "e_inc_num"]).copy()
    top = snapshot.nlargest(12, "e_inc_num")[
        ["country", "g_whoregion", "e_inc_num", "e_inc_100k", "c_newinc", "c_cdr", "notification_gap_num_nonnegative"]
    ].rename(columns={
        "country": "Country", "g_whoregion": "WHO region", "e_inc_num": "Estimated cases",
        "e_inc_100k": "Incidence /100k", "c_newinc": "Notified cases", "c_cdr": "Coverage %",
        "notification_gap_num_nonnegative": "Notification difference",
    })
    st.dataframe(
        top.style.format({
            "Estimated cases": "{:,.0f}", "Incidence /100k": "{:,.1f}", "Notified cases": "{:,.0f}",
            "Coverage %": "{:,.1f}", "Notification difference": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
