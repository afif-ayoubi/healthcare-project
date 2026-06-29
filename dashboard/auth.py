from __future__ import annotations

import os

import streamlit as st


def password_gate() -> None:
    """Optional password screen. It is disabled when APP_PASSWORD is not configured."""
    expected = os.getenv("APP_PASSWORD", "")
    if not expected:
        try:
            expected = str(st.secrets.get("APP_PASSWORD", ""))
        except Exception:
            expected = ""
    if not expected:
        return
    if st.session_state.get("authenticated"):
        return
    st.markdown(
        '<div class="hero"><div class="eyebrow">Protected analytics tool</div>'
        '<h1>Global Tuberculosis Dashboard</h1><p>Enter the project password to continue.</p></div>',
        unsafe_allow_html=True,
    )
    entered = st.text_input("Password", type="password")
    if st.button("Open dashboard", type="primary"):
        if entered == expected:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()
