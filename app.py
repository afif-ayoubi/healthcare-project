from __future__ import annotations

import streamlit as st

from dashboard.auth import password_gate
from dashboard.config import PAGE_CONFIG
from dashboard.data import load_data
from dashboard.filters import render_sidebar
from dashboard.layout import render_footer, render_hero, render_scope_caption
from dashboard.one_page import render_one_page_dashboard
from dashboard.styles import apply_global_styles


def main() -> None:
    st.set_page_config(**PAGE_CONFIG)
    apply_global_styles()
    password_gate()

    data = load_data()
    state = render_sidebar(data)
    render_hero()
    render_scope_caption(state)
    render_one_page_dashboard(data, state)

    render_footer()


main()
