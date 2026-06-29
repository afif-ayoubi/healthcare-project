from __future__ import annotations

import streamlit as st

from dashboard.auth import password_gate
from dashboard.config import PAGE_CONFIG, TAB_LABELS
from dashboard.data import load_data
from dashboard.filters import render_sidebar
from dashboard.layout import render_footer, render_hero, render_scope_caption
from dashboard.styles import apply_global_styles
from dashboard.tabs.age_sex import render_age_sex_tab
from dashboard.tabs.executive import render_executive_tab
from dashboard.tabs.forecast_data import render_forecast_data_tab
from dashboard.tabs.map import render_map_tab
from dashboard.tabs.tb_hiv_resistance import render_tb_hiv_resistance_tab
from dashboard.tabs.trends import render_trends_tab


def main() -> None:
    st.set_page_config(**PAGE_CONFIG)
    apply_global_styles()
    password_gate()

    data = load_data()
    state = render_sidebar(data)
    render_hero()
    render_scope_caption(state)

    tabs = st.tabs(TAB_LABELS)
    with tabs[0]:
        render_executive_tab(data, state)
    with tabs[1]:
        render_map_tab(data, state)
    with tabs[2]:
        render_trends_tab(data, state)
    with tabs[3]:
        render_age_sex_tab(data, state)
    with tabs[4]:
        render_tb_hiv_resistance_tab(data, state)
    with tabs[5]:
        render_forecast_data_tab(data, state)

    render_footer()


main()
