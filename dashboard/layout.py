from __future__ import annotations

import streamlit as st

from dashboard.filters import SelectionState


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">MSBA382 · Healthcare Analytics</div>
          <h1>Global Tuberculosis Burden & Treatment Gaps</h1>
          <p>Explore where TB burden is concentrated, how incidence and mortality have changed, who is most affected, and where diagnosis-and-treatment coverage remains incomplete.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scope_caption(state: SelectionState) -> None:
    st.caption(
        f"Current analytical scope: **{state.selection}** · trend window "
        f"**{state.trend_range[0]}–{state.trend_range[1]}** · map/ranking year **{state.map_year}**"
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
        <b>Source:</b> WHO Global Tuberculosis Programme data and WHO Global Tuberculosis Report 2025-related public data resources. 
        This educational dashboard is for population-health analytics, not diagnosis or clinical decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )
