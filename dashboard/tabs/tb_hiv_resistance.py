from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.data import DashboardData
from dashboard.figures import style_figure
from dashboard.filters import SelectionState
from dashboard.formatting import fmt_count, fmt_pct


def render_tb_hiv_resistance_tab(data: DashboardData, state: SelectionState) -> None:
    latest = state.latest
    st.subheader("TB–HIV co-epidemic and rifampicin/multidrug resistance")
    hiv_cols = st.columns(4)
    hiv_cols[0].metric("HIV-associated incident TB", fmt_count(latest.get("e_inc_tbhiv_num")))
    hiv_cols[1].metric("HIV-associated share", fmt_pct(latest.get("hiv_incidence_share_pct")))
    hiv_cols[2].metric("TB deaths among people with HIV", fmt_count(latest.get("e_mort_tbhiv_num")))
    hiv_cols[3].metric("Estimated RR/MDR-TB incidence", fmt_count(latest.get("e_inc_rr_num")))

    current = data.country[data.country["year"] == state.map_year].copy()
    left, right = st.columns(2)
    with left:
        top_hiv = current.dropna(subset=["e_inc_tbhiv_num"]).nlargest(12, "e_inc_tbhiv_num").sort_values("e_inc_tbhiv_num")
        fig = px.bar(
            top_hiv,
            x="e_inc_tbhiv_num",
            y="country",
            orientation="h",
            color="hiv_incidence_share_pct",
            color_continuous_scale="Purples",
            title="Countries with the largest HIV-associated TB burden",
            labels={"e_inc_tbhiv_num": "Estimated cases", "country": "", "hiv_incidence_share_pct": "Share %"},
        )
        fig.update_xaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)
    with right:
        top_rr = current.dropna(subset=["e_inc_rr_num"]).nlargest(12, "e_inc_rr_num").sort_values("e_inc_rr_num")
        fig = px.bar(
            top_rr,
            x="e_inc_rr_num",
            y="country",
            orientation="h",
            color="rr_incidence_share_pct",
            color_continuous_scale="Magenta",
            title="Countries with the largest estimated RR/MDR-TB burden",
            labels={"e_inc_rr_num": "Estimated cases", "country": "", "rr_incidence_share_pct": "Share %"},
        )
        fig.update_xaxes(tickformat="~s")
        st.plotly_chart(style_figure(fig, 500), use_container_width=True)

    st.markdown(
        '<div class="warning-note"><b>Clinical distinction:</b> HIV increases the risk that latent TB infection progresses to active disease because it weakens immunity. '
        'RR/MDR-TB is different: it refers to resistance to key anti-TB medicines and creates a more difficult treatment pathway.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    scatter_data = current.dropna(subset=["e_inc_100k", "hiv_incidence_share_pct", "e_inc_num"]).copy()
    fig = px.scatter(
        scatter_data,
        x="e_inc_100k",
        y="hiv_incidence_share_pct",
        size="e_inc_num",
        color="g_whoregion",
        hover_name="country",
        size_max=55,
        log_x=True,
        title="Incidence intensity and HIV-associated share",
        labels={"e_inc_100k": "TB incidence per 100,000 (log scale)", "hiv_incidence_share_pct": "HIV-associated share (%)", "g_whoregion": "WHO region"},
    )
    st.plotly_chart(style_figure(fig, 500), use_container_width=True)
